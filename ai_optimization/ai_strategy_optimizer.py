#AI 최적화 시스템에서 직접 매매 신호를 생성하여 실전 트레이딩과 연결
#랜덤 신호가 아닌 AI 모델(ai_optimization/ai_model.py)에서 학습한 최적 신호 사용

import logging
from ai_optimization.ai_model import AIModel
from ai_optimization.data_feed import DataFeed

class AIStrategyOptimizer:
    def __init__(self, api_url: str):
        """
        AI 기반 매매 전략 최적화
        :param api_url: 실시간 데이터 API 주소
        """
        self.data_feed = DataFeed(api_url)
        self.ai_model = AIModel()
        logging.basicConfig(level=logging.INFO)

    def generate_ai_signal(self):
        """ AI 기반 최적 매매 신호 생성 """
        df = self.data_feed.get_market_data()
        if df is not None:
            prediction = self.ai_model.predict(df)
            signal = "BUY" if prediction[0] == 1 else "SELL"
            logging.info(f"📈 AI Optimized Signal: {signal}")
            return signal
        return None

# 사용 예시
if __name__ == "__main__":
    optimizer = AIStrategyOptimizer("https://api.binance.com/api/v3/ticker/24hr")
    print(optimizer.generate_ai_signal())

