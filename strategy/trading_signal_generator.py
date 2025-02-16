# AI 최적화 시스템(ai_optimization/ai_real_time_optimizer.py)에서 생성한 신호를 기반으로 매매 신호 생성
# 기존 단순 전략을 AI 실시간 최적화 시스템과 연결

import logging
from ai_optimization.ai_real_time_optimizer import AIRealTimeOptimizer

class TradingSignalGenerator:
    def __init__(self, api_url: str):
        self.ai_optimizer = AIRealTimeOptimizer(api_url)
        logging.basicConfig(level=logging.INFO)

    def generate_signal(self):
        """ AI 실시간 최적화된 매매 신호 반환 """
        return self.ai_optimizer.update_strategy()

# 사용 예시
if __name__ == "__main__":
    signal_generator = TradingSignalGenerator("https://api.binance.com/api/v3/ticker/24hr")
    print(f"📈 생성된 AI 최적화 매매 신호: {signal_generator.generate_signal()}")
