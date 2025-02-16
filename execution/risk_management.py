# 손절 (Stop-Loss) 및 익절 (Take-Profit) 자동 조정
# 계좌 잔고 변화 감지 추후 리밸런싱 로직 추가

import logging
from binance.client import Client

class RiskManagement:
    def __init__(self, client: Client, symbol: str, balance_threshold: float):
        self.client = client
        self.symbol = symbol
        self.balance_threshold = balance_threshold
        logging.basicConfig(level=logging.INFO)

    def check_account_balance(self):
        """ 계좌 잔고 확인 """
        account_info = self.client.get_account()
        balances = {b["asset"]: float(b["free"]) for b in account_info["balances"]}
        logging.info(f"Current Account Balances: {balances}")
        return balances

    def set_stop_loss(self, price: float, quantity: float):
        """ 손절 주문 실행 """
        try:
            order = self.client.create_order(
                symbol=self.symbol,
                side="SELL",
                type="STOP_LOSS_LIMIT",
                quantity=quantity,
                price=str(price),
                stopPrice=str(price * 0.99)  # 1% 손절
            )
            logging.info(f"Stop Loss Order Placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Stop Loss Order Failed: {e}")
            return None
