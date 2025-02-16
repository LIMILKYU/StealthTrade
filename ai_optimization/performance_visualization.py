# 트레이딩 성과 데이터를 차트로 시각화
# 수익률, 손익비, 최대 손실(MDD), 샤프비율을 그래프로 표현

import pandas as pd
import matplotlib.pyplot as plt
import logging

class PerformanceVisualization:
    def __init__(self, trade_log_file: str):
        self.trade_log_file = trade_log_file
        logging.basicConfig(level=logging.INFO)

    def plot_performance(self):
        """ 트레이딩 성과 차트 시각화 """
        df = pd.read_csv(self.trade_log_file)
        df["PnL"] = df["exit_price"] - df["entry_price"]
        df["Cumulative_PnL"] = df["PnL"].cumsum()

        # 1️⃣ 누적 손익 그래프
        plt.figure(figsize=(10, 5))
        plt.plot(df["Cumulative_PnL"], label="Cumulative PnL", color="blue")
        plt.xlabel("Trades")
        plt.ylabel("PnL (Profit & Loss)")
        plt.title("AI Trading Performance")
        plt.legend()
        plt.grid()
        plt.show()

# 사용 예시
if __name__ == "__main__":
    visualizer = PerformanceVisualization("data/trade_log.csv")
    visualizer.plot_performance()
