import numpy as np
import pandas as pd

class StrategyEvaluator:
    def __init__(self, trading_data):
        """
        매매 전략 평가 클래스
        :param trading_data: DataFrame (매매 신호, 수익률, 손절/익절 정보 포함)
        """
        self.trading_data = trading_data

    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        """ 샤프 비율 (Sharpe Ratio) 계산 """
        excess_returns = returns - risk_free_rate / 252
        return np.mean(excess_returns) / np.std(excess_returns)

    def calculate_sortino_ratio(self, returns, risk_free_rate=0.02):
        """ 소르티노 비율 (Sortino Ratio) 계산 """
        downside_returns = returns[returns < 0]
        return np.mean(returns - risk_free_rate / 252) / np.std(downside_returns)

    def calculate_max_drawdown(self, returns):
        """ 최대 손실폭 (MDD) 계산 """
        cumulative = (1 + returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        return drawdown.min()

    def evaluate_performance(self):
        """ 전체 전략 성과 평가 """
        returns = self.trading_data['returns']
        sharpe = self.calculate_sharpe_ratio(returns)
        sortino = self.calculate_sortino_ratio(returns)
        max_drawdown = self.calculate_max_drawdown(returns)

        performance_metrics = {
            "Sharpe Ratio": sharpe,
            "Sortino Ratio": sortino,
            "Max Drawdown": max_drawdown
        }

        return performance_metrics

# 사용 예제
# trade_data = pd.read_csv("trading_signals.csv")
# evaluator = StrategyEvaluator(trade_data)
# print(evaluator.evaluate_performance())
