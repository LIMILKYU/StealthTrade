import logging
import numpy as np
import pandas as pd
from strategy_evaluator import StrategyEvaluator
from trading_signal_generator import TradingSignalGenerator
from ai_optimization.ai_real_time_optimizer import AIRealTimeOptimizer

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
        self.ai_optimizer = AIRealTimeOptimizer()
        logging.basicConfig(level=logging.INFO)

    def get_market_condition(self):
        """
        AI 변동성 분석을 기반으로 시장 상태 감지
        :return: "Strong Bullish", "Weak Bullish", "Range", "Weak Bearish", "Strong Bearish"
        """
        volatility_factor = self.ai_optimizer.get_volatility_factor(self.asset)

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
        시장 상태에 따라 최적의 전략을 선택하여 실행
        """
        market_condition = self.get_market_condition()
        logging.info(f"📌 현재 시장 상태: {market_condition}")

        results = []

        for strategy in self.strategies:
            print(f"\n[실험 실행] 전략: {strategy}")
            signals = self.signal_generator.generate_signals(strategy)
            evaluation = self.evaluator.evaluate_strategy(signals)
            evaluation["strategy"] = strategy
            evaluation["market_condition"] = market_condition
            results.append(evaluation)

        return pd.DataFrame(results)

    def plot_result(self, results):
        """
        실험 결과를 시각화
        :param results: 실험 결과 데이터프레임
        """
        # 예시: ROI, 승률 등 지표를 기반으로 그래프 그리기
        plt.figure(figsize=(12, 6))
        sns.barplot(x="strategy", y="ROI", data=results)
        plt.title("Strategy Performance - ROI")
        plt.show()

# ✅ 사용 예시
if __name__ == "__main__":
    strategies = ["RSI + SMA", "MACD + EMA", "AI Optimized Strategy"]
    strategy_optimizer = StrategyOptimizer(asset="BTCUSDT", strategies=strategies)

    # 전략 실험 실행
    results = strategy_optimizer.run_experiment()

    # 결과 시각화
    strategy_optimizer.plot_result(results)
