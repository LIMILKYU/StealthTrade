# 승률, 손익비, 최대 손실(MDD) 분석
# 트레이딩 로그 기반 성과 평가

import pandas as pd
import logging

class TradePerformanceAnalyzer:
    def __init__(self, trade_log_file: str):
        self.trade_log_file = trade_log_file
        logging.basicConfig(level=logging.INFO)

    def analyze_performance(self):
        """ 트레이딩 성과 분석 """
        df = pd.read_csv(self.trade_log_file)
        df["PnL"] = df["exit_price"] - df["entry_price"]
        
        win_rate = (df["PnL"] > 0).mean() * 100
        max_drawdown = df["PnL"].min()
        avg_risk_reward = df[df["PnL"] > 0]["PnL"].mean() / abs(df[df["PnL"] < 0]["PnL"].mean())

        logging.info(f"📊 승률: {win_rate:.2f}%, MDD: {max_drawdown:.2f} USDT, 평균 손익비: {avg_risk_reward:.2f}")
        return win_rate, max_drawdown, avg_risk_reward

# 사용 예시
if __name__ == "__main__":
    analyzer = TradePerformanceAnalyzer("data/trade_log.csv")
    analyzer.analyze_performance()
