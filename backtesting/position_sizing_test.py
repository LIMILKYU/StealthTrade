# 켈리 공식(Kelly Criterion) 적용하여 최적 포지션 크기 계산
# 시장 상황 5단계 고려하여 포지션 크기 조절

import logging
from strategy.position_sizing import PositionSizing

class PositionSizingTest:
    def __init__(self, initial_balance: float):
        self.position_sizing = PositionSizing(initial_balance)
        logging.basicConfig(level=logging.INFO)

    def test_position_sizing(self):
        """ 여러 시장 상황에서 포지션 크기 테스트 """
        conditions = ["Strong Bullish", "Weak Bullish", "Range", "Weak Bearish", "Strong Bearish"]
        results = {}

        for condition in conditions:
            self.position_sizing.set_market_condition(condition)
            size = self.position_sizing.calculate_position_size(win_rate=0.6, risk_reward_ratio=2.0, stop_loss_percent=0.01, volatility=1.5, trade_type="LONG")
            results[condition] = size
            logging.info(f"📊 {condition} → Position Size: {size:.2f} USDT")

        return results

# 실행 예시
if __name__ == "__main__":
    tester = PositionSizingTest(10000)
    tester.test_position_sizing()
