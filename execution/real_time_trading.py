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

# ✅ 환경 변수 로드
load_dotenv()

class RealTimeTrading:
    def __init__(self, symbol: str, quantity: float):
        """ 실시간 자동매매 실행 클래스 """
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.secret_key = os.getenv("BINANCE_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            logging.warning("🚨 API 키 없음 → Paper Trading 모드 활성화")
            self.client = None  # 실거래 비활성화
        else:
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
        """ ✅ 실시간 매매 실행 (매매 신호 감지 & 주문 실행) """
        while True:
            try:
                # ✅ 매매 신호 감지
                signal = self.signal_generator.get_signal(self.symbol)
                logging.info(f"📊 매매 신호 감지: {signal}")

                if signal == "BUY":
                    logging.info(f"🚀 매수 주문 실행: {self.symbol} ({self.quantity}개)")
                    order_response = self.place_order("BUY")
                elif signal == "SELL":
                    logging.info(f"🔻 매도 주문 실행: {self.symbol} ({self.quantity}개)")
                    order_response = self.place_order("SELL")
                else:
                    logging.info("⏳ 매매 신호 없음. 다음 신호 대기 중...")

                time.sleep(2)  # ✅ 신호 대기 시간 단축
            except Exception as e:
                logging.error(f"🚨 매매 실행 중 오류 발생: {e}")
                time.sleep(5)  # ✅ 오류 발생 시 5초 대기 후 재시도

    def place_order(self, order_type: str):
        """ ✅ 주문 실행 함수 (API 연동 & 예외 처리 포함) """
        if not self.client:
            logging.warning(f"📢 [PAPER TRADING] {order_type} 주문 실행됨 (실거래 아님)")
            return {"status": "paper_trading", "order_type": order_type}

        try:
            order_response = self.exchange.place_order(self.symbol, order_type, self.quantity, "MARKET")
            logging.info(f"✅ 주문 성공: {order_response}")
            self.telegram_notifier.send_message(f"✅ {self.symbol} {order_type} 주문 완료")
            return order_response
        except requests.RequestException as e:
            logging.error(f"🚨 주문 실패: {e}")
            self.telegram_notifier.send_message(f"🚨 {self.symbol} {order_type} 주문 실패")
            return None
