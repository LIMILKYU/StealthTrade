# 트레이딩 결과를 평가하고 수익률(ROI), 승률, MDD(최대 손실), 샤프비율을 계산
#AI 모델이 실전 트레이딩 결과를 분석하여 전략을 조정할 수 있도록 데이터 제공

import pandas as pd
import numpy as np
import logging

class PerformanceAnalysis:
    def __init__(self, trade_log_file: str):
        """
        :param trade_log_file: 트레이딩 결과가 저장된 로그 파일 (CSV)
        """
        self.trade_log_file = trade_log_file
        logging.basicConfig(level=logging.INFO)

    def analyze_performance(self):
        """ 트레이딩 성과 분석 """
        df = pd.read_csv(self.trade_log_file)
        df["PnL"] = df["exit_price"] - df["entry_price"]

        # 1️⃣ 승률 계산
        win_rate = (df["PnL"] > 0).mean() * 100

        # 2️⃣ 최대 손실 (MDD) 계산
        cumulative_returns = (df["PnL"] / df["entry_price"]).cumsum()
        peak = cumulative_returns.cummax()
        max_drawdown = (cumulative_returns - peak).min()

        # 3️⃣ 평균 손익비 계산
        avg_win = df[df["PnL"] > 0]["PnL"].mean()
        avg_loss = abs(df[df["PnL"] < 0]["PnL"].mean())
        risk_reward_ratio = avg_win / avg_loss if avg_loss != 0 else np.nan

        # 4️⃣ 샤프비율 계산 (리스크 조정된 수익률)
        roi = cumulative_returns.iloc[-1]
        daily_volatility = df["PnL"].std()
        sharpe_ratio = roi / daily_volatility if daily_volatility != 0 else np.nan

        logging.info(f"📊 승률: {win_rate:.2f}%, MDD: {max_drawdown:.2f}, 손익비: {risk_reward_ratio:.2f}, 샤프비율: {sharpe_ratio:.2f}")

        return {
            "win_rate": win_rate,
            "max_drawdown": max_drawdown,
            "risk_reward_ratio": risk_reward_ratio,
            "sharpe_ratio": sharpe_ratio
        }

# 사용 예시
if __name__ == "__main__":
    analyzer = PerformanceAnalysis("data/trade_log.csv")
    print(analyzer.analyze_performance())

