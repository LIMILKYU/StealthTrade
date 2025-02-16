# 트레이딩 성과 분석 결과를 실시간 AI 최적화 시스템에 반영
# AI가 자동으로 전략을 수정하고 지속적으로 학습

import logging
from ai_optimization.ai_model import LSTMAIModel
from ai_optimization.reinforcement_learning import DQNAgent
from ai_optimization.data_feed import DataFeed
from ai_optimization.strategy_feedback import StrategyFeedback

class AIRealTimeOptimizer:
    def __init__(self, api_url: str, trade_log_file: str):
        self.data_feed = DataFeed(api_url)
        self.lstm_model = LSTMAIModel(input_shape=(50, 5))
        self.rl_agent = DQNAgent(state_size=5, action_size=2)
        self.strategy_feedback = StrategyFeedback(trade_log_file)
        logging.basicConfig(level=logging.INFO)

    def update_strategy(self):
        """ 실시간 데이터를 기반으로 전략 최적화 및 성과 피드백 """
        self.strategy_feedback.update_strategy()  # 전략 업데이트 반영
        df = self.data_feed.get_market_data()

        if df is not None:
            prediction = self.lstm_model.predict(df.values.reshape(1, 50, 5))
            signal = "BUY" if prediction[0] == 1 else "SELL"
            action = self.rl_agent.act(df.iloc[-1].values)
            optimized_signal = "BUY" if action == 1 else "SELL"

            logging.info(f"📈 AI Signal: {signal}, RL Optimized Signal: {optimized_signal}")

            return optimized_signal

        return None

# 사용 예시
if __name__ == "__main__":
    optimizer = AIRealTimeOptimizer("https://api.binance.com/api/v3/ticker/24hr", "data/trade_log.csv")
    print(optimizer.update_strategy())

