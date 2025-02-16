# 실제 주문 대신 페이퍼 트레이딩 실행

import logging
from strategy.trading_signal_generator import TradingSignalGenerator
from paper_trading.paper_order_executor import PaperOrderExecutor
from paper_trading.pnl_tracking import PnLTracker
from paper_trading.paper_trading_logger import PaperTradingLogger

class PaperTrader:
    def __init__(self, initial_balance: float, symbol: str, strategy):
        """
        :param initial_balance: 초기 자본금
        :param symbol: 거래할 코인 심볼
        :param strategy: 사용할 매매 전략 객체
        """
        self.balance = initial_balance
        self.symbol = symbol
        self.strategy = strategy  # 매매 전략 연결
        self.order_executor = PaperOrderExecutor(symbol)  # 페이퍼 트레이딩 전용 실행기 사용
        self.pnl_tracker = PnLTracker(initial_balance)
        self.logger = PaperTradingLogger("paper_trading_log.csv")
        logging.basicConfig(level=logging.INFO)

    def execute_trade(self):
        """ 매매 전략에서 신호를 받아 가상 주문 실행 """
        signal = self.strategy.generate_signal()
        if signal:
            trade = self.order_executor.execute_trade(signal, self.balance * 0.1)  # 자본금의 10% 사용
            self.pnl_tracker.execute_trade(signal, trade["price"], trade["size"])
            self.logger.log_trade(self.symbol, signal, trade["price"], trade["size"])

    def run(self):
        """ 페이퍼 트레이딩 실행 루프 """
        logging.info("🚀 Paper Trading Started!")
        while True:
            self.execute_trade()

# 사용 예시
if __name__ == "__main__":
    strategy = TradingSignalGenerator()
    trader = PaperTrader(10000, "BTCUSDT", strategy)
    trader.run()
