import numpy as np
import pandas as pd
from trading_signal_generator import TradingSignalGenerator
from backtesting import Backtest

class StrategyEvaluator:
    def __init__(self, market_data, initial_balance=10000):
        """
        매매 전략 평가 클래스
        :param market_data: 시장 데이터 (DataFrame 형식)
        :param initial_balance: 초기 투자 금액 (기본값 10000)
        """
        self.market_data = market_data
        self.initial_balance = initial_balance
        self.signals = None
        self.backtest_results = None
    
    def evaluate_strategy(self):
        """
        매매 전략을 백테스트하고 성과 지표를 평가함
        """
        # 1️⃣ 매매 신호 생성
        signal_generator = TradingSignalGenerator(self.market_data)
        self.signals = signal_generator.generate_signals()
        
        # 2️⃣ 백테스트 실행
        bt = Backtest(self.market_data, self.signals)
        self.backtest_results = bt.run()
        
        # 3️⃣ 핵심 성과 지표 계산
        performance_metrics = {
            'Total Return': self.backtest_results['total_return'],
            'Sharpe Ratio': self.backtest_results['sharpe_ratio'],
            'Max Drawdown': self.backtest_results['max_drawdown'],
            'Win Rate': self.backtest_results['win_rate'],
            'Profit Factor': self.backtest_results['profit_factor']
        }
        
        return performance_metrics
    
    def get_backtest_results(self):
        """
        백테스트 결과 반환
        """
        return self.backtest_results

# 사용 예시
# market_data = pd.read_csv('market_data.csv')
# evaluator = StrategyEvaluator(market_data)
# results = evaluator.evaluate_strategy()
# print(results)
