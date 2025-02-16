# 매매 기록을 로깅
# CSV 또는 데이터베이스에 저장

import csv
import logging

class TradeLogger:
    def __init__(self, log_file="trade_log.csv"):
        self.log_file = log_file
        logging.basicConfig(level=logging.INFO)

    def log_trade(self, symbol, side, price, quantity, timestamp):
        """ 거래 내역 기록 """
        with open(self.log_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, symbol, side, price, quantity])
        logging.info(f"Trade logged: {symbol}, {side}, {price}, {quantity}")

# 사용 예시
if __name__ == "__main__":
    logger = TradeLogger()
    logger.log_trade("BTCUSDT", "BUY", 50000, 0.01, "2025-02-16 12:00:00")
