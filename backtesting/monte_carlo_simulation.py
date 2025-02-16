# 전략의 확률적 성과 평가
# 1,000번 이상의 시뮬레이션을 수행하여 수익률 변동성 분석
# 전략이 장기적으로 수익성이 있는지 검증

import numpy as np
import matplotlib.pyplot as plt
import logging

class MonteCarloSimulation:
    def __init__(self, initial_balance: float, win_rate: float, risk_reward_ratio: float, num_simulations: int = 1000, num_trades: int = 100):
        """
        :param initial_balance: 초기 자본금 (예: 10,000 USDT)
        :param win_rate: 승률 (예: 0.6 = 60%)
        :param risk_reward_ratio: 손익비 (예: 2.0 = 1:2)
        :param num_simulations: 실행할 시뮬레이션 횟수 (기본: 1000번)
        :param num_trades: 각 시뮬레이션에서 수행할 트레이드 횟수 (기본: 100회)
        """
        self.initial_balance = initial_balance
        self.win_rate = win_rate
        self.risk_reward_ratio = risk_reward_ratio
        self.num_simulations = num_simulations
        self.num_trades = num_trades
        logging.basicConfig(level=logging.INFO)

    def run_simulation(self):
        """ 몬테카를로 시뮬레이션 실행 """
        final_balances = []

        for _ in range(self.num_simulations):
            balance = self.initial_balance
            for _ in range(self.num_trades):
                if np.random.rand() < self.win_rate:
                    balance *= (1 + self.risk_reward_ratio * 0.02)  # 수익 발생
                else:
                    balance *= (1 - 0.02)  # 손실 발생
            final_balances.append(balance)

        return final_balances

    def plot_results(self):
        """ 시뮬레이션 결과 시각화 """
        results = self.run_simulation()
        plt.figure(figsize=(8, 5))
        plt.hist(results, bins=50, alpha=0.75, color="blue", edgecolor="black")
        plt.axvline(self.initial_balance, color="red", linestyle="dashed", linewidth=2, label="Initial Balance")
        plt.xlabel("Final Balance")
        plt.ylabel("Frequency")
        plt.title(f"Monte Carlo Simulation Results ({self.num_simulations} Runs)")
        plt.legend()
        plt.grid(True)
        plt.show()

# 실행 예시
if __name__ == "__main__":
    simulation = MonteCarloSimulation(10000, win_rate=0.6, risk_reward_ratio=2.0)
    simulation.plot_results()
