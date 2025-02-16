# 실시간 손익(PnL) 계산
# 계좌 잔고 변화를 추적

import logging

class PnLTracker:
    def __init__(self, initial_balance: float):
        """
        :param initial_balance: 초기 자본금
        """
        self.balance = initial_balance
        self.trades = []
        logging.basicConfig(level=logging.INFO)

    def execute_trade(self, trade_type: str, price: float, size: float):
        """ 매매 실행 후 손익 계산 """
        trade = {"type": trade_type, "price": price, "size": size}
        self.trades.append(trade)

        if trade_type == "BUY":
            self.balance -= size
        else:
            self.balance += size * 1.02  # 2% 수익 가정

        logging.info(f"💰 New Balance: {self.balance:.2f} USDT")

# 사용 예시
if __name__ == "__main__":
    pnl_tracker = PnLTracker(10000)
    pnl_tracker.execute_trade("BUY", 50000, 1000)
    pnl_tracker.execute_trade("SELL", 50200, 1000)
