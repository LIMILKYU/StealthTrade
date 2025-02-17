import requests
import logging
import os
from dotenv import load_dotenv
from strategy.trading_signal_generator import TradingSignalGenerator
from backend.t_rpc_client import tRPCClient
from notification.telegram_notifier import TelegramNotifier

# 환경 변수 로드
load_dotenv()

class ExchangeAccount:
    def __init__(self):
        """ 거래소 API를 사용하여 계정 정보를 가져오는 클래스 """
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.secret_key = os.getenv("BINANCE_SECRET_KEY")
        self.base_url = "https://api.binance.com"
        self.headers = {"X-MBX-APIKEY": self.api_key}
        self.trpc_client = tRPCClient(os.getenv("TRPC_API_URL"))
        self.telegram_notifier = TelegramNotifier(
            os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
        )
        logging.basicConfig(level=logging.INFO)

    def get_account_balance(self):
        """ 내 계정의 총 자본금 및 잔액 조회 """
        try:
            url = f"{self.base_url}/api/v3/account"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                balances = {asset["asset"]: float(asset["free"]) for asset in data["balances"]}
                return balances
            else:
                logging.error(f"❌ 계정 정보 불러오기 실패: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"⚠️ API 요청 오류 발생: {e}")
            return None

    def place_order(self, symbol, side, quantity, order_type="LIMIT", price=None):
        """ 주문 실행 및 체결 내역 업데이트 """
        try:
            order_data = {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
            }
            if order_type == "LIMIT" and price:
                order_data["price"] = price
                order_data["timeInForce"] = "GTC"  # 지정가 주문 유지

            url = f"{self.base_url}/api/v3/order"
            response = requests.post(url, headers=self.headers, json=order_data)

            if response.status_code == 200:
                order_response = response.json()
                order_id = order_response["orderId"]
                logging.info(f"✅ 주문 체결 성공: {order_id}")

                # 주문 체결 후 데이터 동기화
                self.sync_order_status(order_id, symbol)

                # 주문 성공 알림 전송
                self.telegram_notifier.send_message(
                    f"📌 **주문 체결 완료**\n"
                    f"🔹 종목: {symbol}\n"
                    f"🔹 방향: {side}\n"
                    f"🔹 수량: {quantity}\n"
                    f"🔹 주문 유형: {order_type}\n"
                    f"🔹 주문 ID: {order_id}"
                )
                return order_response
            else:
                logging.error(f"🚨 주문 실패: {response.text}")
                self.telegram_notifier.send_message(f"❌ 주문 실패: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"⚠️ API 오류 발생: {e}")
            self.telegram_notifier.send_message(f"⚠️ 주문 실행 실패! API 오류 발생\n{e}")
            return None

    def sync_order_status(self, order_id, symbol):
        """ 주문 체결 상태 확인 후 프론트엔드 데이터 동기화 """
        try:
            url = f"{self.base_url}/api/v3/order?symbol={symbol}&orderId={order_id}"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                order_status = response.json()
                logging.info(f"📌 주문 상태 확인 완료: {order_status['status']}")

                # tRPC API를 통해 프론트엔드 업데이트
                self.trpc_client.update_trade_data({
                    "symbol": symbol,
                    "order_id": order_id,
                    "status": order_status["status"],
                    "executed_qty": order_status["executedQty"],
                    "side": order_status["side"],
                })

                if order_status["status"] == "FILLED":
                    self.telegram_notifier.send_message(f"✅ **주문 완전 체결**: {symbol}, 주문 ID: {order_id}")
                elif order_status["status"] == "PARTIALLY_FILLED":
                    self.telegram_notifier.send_message(f"⚠️ **부분 체결**: {symbol}, 주문 ID: {order_id}")

            else:
                logging.error(f"🚨 주문 상태 조회 실패: {response.text}")

        except requests.exceptions.RequestException as e:
            logging.error(f"⚠️ 주문 상태 동기화 중 API 오류 발생: {e}")

if __name__ == "__main__":
    exchange = ExchangeAccount()
    exchange.place_order("BTCUSDT", "BUY", 0.01, "LIMIT", 45000.0)
