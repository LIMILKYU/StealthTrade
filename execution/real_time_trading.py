import logging
import time
import os
import requests
from dotenv import load_dotenv
from binance.client import Client
from execution.order_executor import ExchangeAccount
from strategy.trading_signal_generator import TradingSignalGenerator
from backend.t_rpc_client import tRPCClient
from notification.telegram_notifier import TelegramNotifier

# 환경 변수 로드
load_dotenv()

class RealTimeTrading:
    def __init__(self, symbol: str, quantity: float):
        """ 실시간 자동매매 실행 클래스 """
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.secret_key = os.getenv("BINANCE_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            raise ValueError("🚨 API 키가 설정되지 않았습니다! .env 파일을 확인하세요.")

        self.client = Client(self.api_key, self.secret_key)
        self.symbol = symbol
        self.quantity = quantity
        self.exchange = ExchangeAccount()
        self.signal_generator = TradingSignalGenerator()
        self.trpc_client = tRPCClient(os.getenv("TRPC_API_URL"))
        self.telegram_notifier = TelegramNotifier(
            os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
        )

        logging.basicConfig(level=logging.INFO)

    def execute_trade(self):
        """ 실시간 매매 실행 (매매 신호 감지 & 주문 실행) """
        while True:
            try:
                signal = self.signal_generator.get_signal(self.symbol)
                logging.info(f"📊 매매 신호 감지: {signal}")

                if signal == "BUY":
                    logging.info(f"🚀 매수 주문 실행: {self.symbol} ({self.quantity}개)")
                    order_response = self.exchange.place_order(self.symbol, "BUY", self.quantity, "MARKET")
                elif signal == "SELL":
                    logging.info(f"🔻 매도 주문 실행: {self.symbol} ({self.quantity}개)")
                    order_response = self.exchange.place_order(self.symbol, "SELL", self.quantity, "MARKET")
                else:
                    logging.info("⏳ 매매 신호 없음. 다음 신호 대기 중...")
                    time.sleep(5)
                    continue

                if order_response:
                    order_id = order_response.get("orderId", "N/A")
                    status = order_response.get("status", "UNKNOWN")

                    # 주문 체결 정보 업데이트
                    self.trpc_client.update_trade_data({
                        "symbol": self.symbol,
                        "order_id": order_id,
                        "status": status,
                        "side": signal,
                        "quantity": self.quantity
                    })

                    # 텔레그램 알림 전송
                    self.telegram_notifier.send_message(
                        f"📌 **자동매매 주문 실행**\n"
                        f"✅ 종목: {self.symbol}\n"
                        f"✅ 방향: {signal}\n"
                        f"✅ 수량: {self.quantity}\n"
                        f"✅ 주문 상태: {status}\n"
                        f"📊 주문 ID: {order_id}"
                    )

                time.sleep(5)  # 5초 후 다음 신호 확인

            except requests.exceptions.RequestException as e:
                logging.error(f"⚠️ API 요청 실패: {e}")
                time.sleep(10)

if __name__ == "__main__":
    SYMBOL = os.getenv("DEFAULT_TRADING_PAIR", "BTCUSDT")
    QUANTITY = 0.01  # 기본 수량 설정
    trading_bot = RealTimeTrading(SYMBOL, QUANTITY)
    trading_bot.execute_trade()
