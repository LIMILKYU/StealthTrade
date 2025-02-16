# 최적의 승률(Win Rate)과 손익비(Risk-Reward Ratio) 찾기
# 백테스트 결과를 기반으로 가장 높은 기대수익을 주는 파라미터 조정
# Grid Search를 사용하여 전략 최적화

import numpy as np
import pandas as pd
import logging
from itertools import product

class StrategyOptimizer:
    def __init__(self, trade_log_file: str):
        """
        :param trade_log_file: 백테스트 결과 파일 (CSV)
        """
        self.trade_log_file = trade_log_file
        self.best_params = None
        logging.basicConfig(level=logging.INFO)

    def load_trade_data(self):
        """ 트레이딩 로그 데이터 로드 """
        try:
            df = pd.read_csv(self.trade_log_file)
            df["PnL"] = df["exit_price"] - df["entry_price"]
            return df
        except Exception as e:
            logging.error(f"🚨 Error Loading Trade Data: {e}")
            return None

    def optimize_strategy(self):
        """ 전략 최적화 실행 (최적의 승률과 손익비 찾기) """
        df = self.load_trade_data()
        if df is None:
            return None

        # 최적화할 범위 설정
        win_rates = np.linspace(0.4, 0.8, 5)  # 40% ~ 80%
        risk_reward_ratios = np.linspace(1.5, 3.0, 5)  # 1.5:1 ~ 3:1

        best_performance = -np.inf
        best_params = None

        for win_rate, risk_reward_ratio in product(win_rates, risk_reward_ratios):
            expected_pnl = self.calculate_expected_pnl(df, win_rate, risk_reward_ratio)
            if expected_pnl > best_performance:
                best_performance = expected_pnl
                best_params = (win_rate, risk_reward_ratio)

        self.best_params = best_params
        logging.info(f"✅ Best Parameters Found: Win Rate = {best_params[0]:.2f}, Risk-Reward Ratio = {best_params[1]:.2f}")
        return best_params

    def calculate_expected_pnl(self, df, win_rate, risk_reward_ratio):
        """ 기대 PnL 계산 """
        win_trades = df[df["PnL"] > 0]
        loss_trades = df[df["PnL"] < 0]

        avg_win = win_trades["PnL"].mean() * risk_reward_ratio
        avg_loss = abs(loss_trades["PnL"].mean())

        expected_pnl = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        return expected_pnl

# 실행 예시
if __name__ == "__main__":
    optimizer = StrategyOptimizer("data/trade_log.csv")
    optimizer.optimize_strategy()
