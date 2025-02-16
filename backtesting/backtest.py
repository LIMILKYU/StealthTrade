# 과거 데이터 로드 및 전략 실행
# 손익(PnL) 및 수익률 계산
# 트레이딩 로그 저장

import pandas as pd
import logging

class Backtester:
    def __init__(self, data_file: str, initial_balance: float):
        """
        :param data_file: CSV 또는 JSON 형식의 과거 데이터 파일
        :param initial_balance: 초기 자본금 (예: 10,000 USDT)
        """
        self.data_file = data_file
        self.balance = initial_balance
        self.trades = []
        logging.basicConfig(level=logging.INFO)

    def load_data(self):
        """ 과거 데이터 로드 """
        try:
            df = pd.read_csv(self.data_file)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            logging.info(f"✅ Data Loaded: {self.data_file}, Rows: {len(df)}")
            return df
        except Exception as e:
            logging.error(f"🚨 Error Loading Data: {e}")
            return None

    def run_backtest(self, strategy):
        """ 백테스트 실행 """
        df = self.load_data()
        if df is None:
            return

        for _, row in df.iterrows():
            signal = strategy(row)
            if signal:
                self.execute_trade(signal, row["price"], row["timestamp"])

        self.calculate_performance()

    def execute_trade(self, trade_type: str, price: float, timestamp: str):
        """ 주문 실행 및 잔고 업데이트 """
        position_size = self.balance * 0.1  # 예제: 자본금의 10% 사용
        self.trades.append({"timestamp": timestamp, "type": trade_type, "price": price, "size": position_size})
        logging.info(f"📈 Trade Executed: {trade_type} at {price} USDT, Size: {position_size} USDT")

    def calculate_performance(self):
        """ 성과 분석 (PnL 계산) """
        pnl = sum([t["size"] * 0.02 for t in self.trades])  # 예제: 각 거래에서 2% 수익 가정
        logging.info(f"📊 Total PnL: {pnl:.2f} USDT")
        return pnl

# 사용 예시
if __name__ == "__main__":
    def simple_strategy(row):
        return "BUY" if row["price"] > row["price"].mean() else None

    backtester = Backtester("data/historical_data.csv", 10000)
    backtester.run_backtest(simple_strategy)
