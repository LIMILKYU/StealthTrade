# 트레이딩 성과 분석 결과를 AI 모델에 피드백하여 자동 최적화
# 강화 학습 모델(DQN)과 LSTM 모델이 학습 데이터로 반영하여 지속 개선

import logging
from ai_optimization.performance_analysis import PerformanceAnalysis
from ai_optimization.reinforcement_learning import DQNAgent
from ai_optimization.ai_model import LSTMAIModel

class StrategyFeedback:
    def __init__(self, trade_log_file: str):
        self.performance_analyzer = PerformanceAnalysis(trade_log_file)
        self.dqn_agent = DQNAgent(state_size=5, action_size=2)
        self.lstm_model = LSTMAIModel(input_shape=(50, 5))
        logging.basicConfig(level=logging.INFO)

    def update_strategy(self):
        """ 트레이딩 성과 분석을 바탕으로 AI 모델 최적화 """
        performance = self.performance_analyzer.analyze_performance()

        if performance["win_rate"] < 50:  # 승률이 낮으면 전략 조정
            logging.warning("⚠️ 승률이 낮음. AI 전략 조정 중...")
            self.dqn_agent.epsilon = max(self.dqn_agent.epsilon * 1.05, 1.0)  # 탐험률 증가

        if performance["max_drawdown"] < -0.05:  # MDD가 -5% 이상이면 방어적인 전략 적용
            logging.warning("⚠️ 손실이 크므로 방어적 전략으로 변경...")
            self.dqn_agent.gamma = 0.85  # 할인율 낮춰 보수적인 매매로 조정

        logging.info("✅ AI 전략 업데이트 완료!")

# 사용 예시
if __name__ == "__main__":
    feedback = StrategyFeedback("data/trade_log.csv")
    feedback.update_strategy()
