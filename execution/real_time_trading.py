# 매매 신호를 감지하여 자동으로 주문 실행
# 트레이딩 전략을 적용하여 포지션 관리

import logging
from binance.client import Client
from execution.order_executor import OrderExecutor
from strategy.trading_signal_generator import TradingSignalGenerator

class RealTimeTrading:
    def __init__(self, client: Client, symbol: str, quantity: float):
        self.client = client
        self.symbol = symbol
        self.quantity = quantity
        self.executor = OrderExecutor(client, symbol, quantity)
        self.signal_generator = TradingSignalGenerator()
        logging.basicConfig(level=logging.INFO)

    def execute_trade(self):
        """ 실시간 매매 실행 """
        signal = self.signal_generator.get_signal(self.symbol)
        logging.info(f"Received Trading Signal: {signal}")

        if signal == "BUY":
            self.executor.place_market_order("BUY")
        elif signal == "SELL":
            self.executor.place_market_order("SELL")
        else:
            logging.info("No valid trading signal.")

if __name__ == "__main__":
    client = Client("API_KEY", "API_SECRET")
    trading_bot = RealTimeTrading(client, "BTCUSDT", 0.01)
    trading_bot.execute_trade()
