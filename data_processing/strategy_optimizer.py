import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from strategy_evaluator import StrategyEvaluator
from trading_signal_generator import TradingSignalGenerator

class StrategyOptimizer:
    def __init__(self, asset="BTCUSDT", interval="1h", strategies=None):
        """
        매매 전략 최적화를 위한 클래스
        :param asset: 분석할 자산 (BTCUSDT 등)
        :param interval: 캔들 간격
        :param strategies: 실험할 전략 목록
        """
        self.asset = asset
        self.interval = interval
        self.strategies = strategies if strategies else []
        self.evaluator = StrategyEvaluator()
        self.signal_generator = TradingSignalGenerator()

    def run_experiment(self):
        """
        각 전략을 실행하고 결과를 비교
        """
        results = []

        for strategy in self.strategies:
            print(f"\n[실험 실행] 전략: {strategy}")
            signals = self.signal_generator.generate_signals(strategy)
            evaluation = self.evaluator.evaluate_strategy(signals)
            evaluation["strategy"] = strategy
            results.append(evaluation)

        return pd.DataFrame(results)

    def plot_results(self, results_df):
        """
        전략별 성과 비교 시각화
        """
        plt.figure(figsize=(12, 6))
        sns.barplot(data=results_df, x="strategy", y="cumulative_return", palette="coolwarm")
        plt.title("전략별 누적 수익률 비교")
        plt.xlabel("전략")
        plt.ylabel("누적 수익률 (%)")
        plt.xticks(rotation=45)
        plt.show()

    def optimize_strategy(self):
        """
        최적의 전략 탐색
        """
        results_df = self.run_experiment()
        print(results_df.sort_values(by="cumulative_return", ascending=False))
        self.plot_results(results_df)

        best_strategy = results_df.loc[results_df["cumulative_return"].idxmax(), "strategy"]
        print(f"\n✅ 최적의 전략: {best_strategy}")
        return best_strategy

# 실행 예제
# optimizer = StrategyOptimizer(strategies=["RSI", "MACD", "Bollinger Bands"])
# best = optimizer.optimize_strategy()
