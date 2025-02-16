# 트레이딩 내역을 CSV 파일로 저장
# 손익 분석을 위한 데이터 관리

import csv
import logging

class PaperTradingLogger:
    def __init__(self, log_file="paper_trading_log.csv"):
        self.log_file = log_file
        logging.basicConfig(level=logging.INFO)

    def log_trade(self, symbol, trade_type, price, size):
        """ 매매 내역 기록 """
        with open(self.log_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([symbol, trade_type, price, size])
        logging.info(f"📝 Trade Logged: {symbol}, {trade_type}, {price} USDT, {size} USDT")

# 사용 예시
if __name__ == "__main__":
    logger = PaperTradingLogger()
    logger.log_trade("BTCUSDT", "BUY", 50000, 1000)
