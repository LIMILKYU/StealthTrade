import logging
import os
from binance.client import Client
from dotenv import load_dotenv

# ✅ 환경 변수 로드
load_dotenv()

class RiskManagement:
    def __init__(self, client: Client, symbol: str, balance_threshold: float):
        """ ✅ 리스크 관리 클래스 (손절, 익절 자동 설정) """
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.secret_key = os.getenv("BINANCE_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            logging.warning("🚨 API 키 없음 → Paper Trading 모드 활성화")
            self.paper_trading = True
            self.client = None
        else:
            self.paper_trading = False
            self.client = client

        self.symbol = symbol
        self.balance_threshold = balance_threshold
        logging.basicConfig(level=logging.INFO)

    def check_account_balance(self):
        """ ✅ 계좌 잔고 확인 """
        if self.paper_trading:
            logging.info("📢 Paper Trading 모드 - 잔액 조회 불가")
            return {"BTC": 100, "USDT": 50000}  # ✅ 테스트 데이터 반환

        try:
            account_info = self.client.get_account()
            balances = {b["asset"]: float(b["free"]) for b in account_info["balances"]}
            logging.info(f"✅ 계좌 잔고 조회 완료: {balances}")
            return balances
        except Exception as e:
            logging.error(f"🚨 계좌 잔고 조회 실패: {e}")
            return None

    def set_stop_loss(self, price: float, quantity: float, atr_multiplier: float = 1.5):
        """ ✅ 변동성 기반 손절 주문 실행 (ATR 적용) """
        stop_loss_price = price - (price * 0.01 * atr_multiplier)  # ATR 기반 손절 설정

        if self.paper_trading:
            logging.info(f"📢 [PAPER TRADING] 손절 주문 실행됨: {stop_loss_price:.2f}")
            return {"status": "paper_trading", "type": "STOP_LOSS_LIMIT", "price": stop_loss_price}

        try:
            order = self.client.create_order(
                symbol=self.symbol,
                side="SELL",
                type="STOP_LOSS_LIMIT",
                quantity=quantity,
                price=str(stop_loss_price),
                stopPrice=str(stop_loss_price * 0.99)
            )
            logging.info(f"✅ 손절 주문 성공: {order}")
            return order
        except Exception as e:
            logging.error(f"🚨 손절 주문 실패: {e}")
            return None

    def set_take_profit(self, price: float, quantity: float, rr_ratio: float = 2.0):
        """ ✅ 손익비(RR Ratio) 기반 익절 주문 실행 """
        take_profit_price = price + ((price * 0.01) * rr_ratio)

        if self.paper_trading:
            logging.info(f"📢 [PAPER TRADING] 익절 주문 실행됨: {take_profit_price:.2f}")
            return {"status": "paper_trading", "type": "TAKE_PROFIT_LIMIT", "price": take_profit_price}

        try:
            order = self.client.create_order(
                symbol=self.symbol,
                side="SELL",
                type="TAKE_PROFIT_LIMIT",
                quantity=quantity,
                price=str(take_profit_price),
                stopPrice=str(take_profit_price * 1.01)
            )
            logging.info(f"✅ 익절 주문 성공: {order}")
            return order
        except Exception as e:
            logging.error(f"🚨 익절 주문 실패: {e}")
            return None
