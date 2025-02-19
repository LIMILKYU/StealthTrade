import pandas as pd
import logging
import os

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
        if not os.path.exists(self.data_file):
            logging.error(f"🚨 데이터 파일을 찾을 수 없습니다: {self.data_file}")
            return None

        try:
            df = pd.read_csv(self.data_file)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            logging.info(f"✅ 데이터 로드 완료: {self.data_file}, 총 {len(df)} 개의 데이터")
            return df
        except Exception as e:
            logging.error(f"🚨 데이터 로딩 오류: {e}")
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

# 실행 예제
if __name__ == "__main__":
    def simple_strategy(row):
        return "BUY" if row["price"] > row["price"].mean() else None

    backtester = Backtester("data/historical_data.csv", 10000)
    backtester.run_backtest(simple_strategy)
