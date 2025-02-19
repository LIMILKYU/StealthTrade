import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from strategy_evaluator import StrategyEvaluator
from trading_signal_generator import TradingSignalGenerator

# ✅ AI 변동성 최적화 객체 생성
ai_optimizer = AIRealTimeOptimizer()

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
        logging.basicConfig(level=logging.INFO)

    def get_market_condition(self):
        """
        ✅ AI 변동성 분석을 기반으로 시장 상태 감지
        :return: "Strong Bullish", "Weak Bullish", "Range", "Weak Bearish", "Strong Bearish"
        """
        volatility_factor = ai_optimizer.get_volatility_factor(self.asset)

        if volatility_factor > 1.5:
            return "Strong Bullish"
        elif 1.2 <= volatility_factor <= 1.5:
            return "Weak Bullish"
        elif 0.8 <= volatility_factor < 1.2:
            return "Range"
        elif 0.5 <= volatility_factor < 0.8:
            return "Weak Bearish"
        else:
            return "Strong Bearish"

    def run_experiment(self):
        """
        ✅ 시장 상태에 따라 최적의 전략을 선택하여 실행
        """
        market_condition = self.get_market_condition()
        logging.info(f"📌 현재 시장 상태: {market_condition}")

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
        plt.legend(title="Market Condition")
        plt.show()

    def optimize_strategy(self):
        """
        최적의 전략 탐색
        """
        results_df = self.run_experiment()
        print(results_df.sort_values(by="cumulative_return", ascending=False))
        self.plot_results(results_df)

        best_strategy = results_df.loc[results_df["cumulative_return"].idxmax(), "strategy"]
        logging.info(f"\n✅ 최적의 전략: {best_strategy} (현재 시장 상태: {self.get_market_condition()})")
        return best_strategy

# 실행 예제
# optimizer = StrategyOptimizer(strategies=["RSI", "MACD", "Bollinger Bands"])
# best = optimizer.optimize_strategy()
