import requests
import logging
import os
from dotenv import load_dotenv
from backend.t_rpc_client import tRPCClient
from notification.telegram_notifier import TelegramNotifier

# ✅ 환경 변수 로드
load_dotenv()

class ExchangeAccount:
    def __init__(self):
        """ ✅ 거래소 API 계정 정보 및 주문 실행 클래스 """
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.secret_key = os.getenv("BINANCE_SECRET_KEY")
        self.base_url = "https://api.binance.com"
        self.headers = {"X-MBX-APIKEY": self.api_key}
        self.trpc_client = tRPCClient(os.getenv("TRPC_API_URL"))
        self.telegram_notifier = TelegramNotifier(
            os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
        )

        # ✅ API 키 없으면 Paper Trading 모드 실행
        if not self.api_key or not self.secret_key:
            logging.warning("🚨 API 키 없음 → Paper Trading 모드 활성화")
            self.paper_trading = True
        else:
            self.paper_trading = False

        logging.basicConfig(level=logging.INFO)

    def get_account_balance(self):
        """ ✅ 내 계정의 총 자본금 및 잔액 조회 """
        if self.paper_trading:
            logging.info("📢 Paper Trading 모드 - 잔액 조회 불가")
            return {"BTC": 100, "USDT": 50000}  # ✅ 테스트 데이터 반환

        try:
            url = f"{self.base_url}/api/v3/account"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            balances = {asset["asset"]: float(asset["free"]) for asset in data["balances"]}
            logging.info(f"✅ 계정 잔고 조회 완료: {balances}")
            return balances
        except requests.RequestException as e:
            logging.error(f"⚠️ API 요청 오류 발생: {e}")
            return None

    def place_order(self, symbol, side, quantity, order_type="MARKET", price=None, time_in_force="GTC"):
        """ ✅ 주문 실행 및 체결 내역 업데이트 """
        if self.paper_trading:
            logging.info(f"📢 Paper Trading 모드 - {side} {symbol} {quantity} 주문 실행됨")
            return {"status": "paper_trading", "order_type": side, "symbol": symbol, "quantity": quantity}

        try:
            order_data = {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
            }
            if order_type == "LIMIT" and price:
                order_data["price"] = price
                order_data["timeInForce"] = time_in_force  # ✅ GTC / IOC / FOK 지원 추가

            url = f"{self.base_url}/api/v3/order"
            response = requests.post(url, headers=self.headers, params=order_data)
            response.raise_for_status()
            order_response = response.json()
            logging.info(f"✅ 주문 성공: {order_response}")
            return order_response
        except requests.RequestException as e:
            logging.error(f"🚨 주문 실패: {e}")
            return None
