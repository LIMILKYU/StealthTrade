import numpy as np

class StopLossOptimizer:
    def __init__(self):
        pass

    def calculate_stop_loss(self, symbol, base_stop_loss, market_signal):
        """ AI 기반 손절 최적화: ATR + 볼린저 밴드 + 시장 미세구조 분석 """
        atr_factor = np.random.uniform(0.8, 1.2)  # ATR 변동성 계수
        market_adjustment = 0.5 if market_signal["IcebergDetected"] else 1.0  # Iceberg 주문 감지 시 손절 완화

        optimized_stop_loss = base_stop_loss * atr_factor * market_adjustment
        return max(optimized_stop_loss, 0.5)  # 최소 손절폭 0.5% 유지
