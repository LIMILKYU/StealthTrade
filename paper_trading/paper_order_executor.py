# 실제 API 호출 없이 가상의 주문 체결
# execution/order_executor.py와 동일한 인터페이스 유지
# 가상의 체결 가격을 반영하여 손익 계산 가능

import logging
from paper_trading.virtual_order_book import VirtualOrderBook

class PaperOrderExecutor:
    def __init__(self, symbol: str):
        """
        페이퍼 트레이딩 전용 주문 실행기
        :param symbol: 거래할 코인 심볼 (예: "BTCUSDT")
        """
        self.symbol = symbol
        self.order_book = VirtualOrderBook(symbol)
        logging.basicConfig(level=logging.INFO)

    def execute_trade(self, trade_type: str, size: float):
        """ 가상의 체결 가격으로 주문 실행 """
        price = self.order_book.get_current_price()
        logging.info(f"📊 Paper Trade Executed: {trade_type} {size} {self.symbol} at {price} USDT")
        return {"trade_type": trade_type, "price": price, "size": size}

# 사용 예시
if __name__ == "__main__":
    executor = PaperOrderExecutor("BTCUSDT")
    executor.execute_trade("BUY", 1000)
    executor.execute_trade("SELL", 1000)
