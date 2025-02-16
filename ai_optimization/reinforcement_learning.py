# Deep Q-Learning(DQN)으로 AI가 스스로 매매 전략을 학습
# 실제 거래 데이터를 활용하여 최적의 매매 신호 생성

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import random
import logging

class DQNAgent:
    def __init__(self, state_size=5, action_size=2):
        """
        :param state_size: 입력 상태 크기 (예: 시장 데이터)
        :param action_size: 행동 크기 (BUY, SELL)
        """
        self.state_size = state_size
        self.action_size = action_size
        self.memory = []
        self.gamma = 0.95  # 할인율
        self.epsilon = 1.0  # 탐험률 (초기에는 무작위 탐색)
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self.build_model()
        logging.basicConfig(level=logging.INFO)

    def build_model(self):
        """ DQN 모델 생성 """
        model = Sequential([
            Dense(24, input_dim=self.state_size, activation="relu"),
            Dense(24, activation="relu"),
            Dense(self.action_size, activation="linear")
        ])
        model.compile(loss="mse", optimizer=tf.keras.optimizers.Adam(lr=self.learning_rate))
        logging.info("✅ DQN Model Built Successfully")
        return model

    def remember(self, state, action, reward, next_state, done):
        """ 학습 데이터 저장 """
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """ 행동 선택 (BUY/SELL) """
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)  # 랜덤 선택 (탐험)
        q_values = self.model.predict(np.array([state]))
        return np.argmax(q_values[0])  # 최적의 행동 선택

    def replay(self, batch_size=32):
        """ 경험 리플레이 학습 """
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward if done else reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
            target_f = self.model.predict(np.array([state]))
            target_f[0][action] = target
            self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# 사용 예시
if __name__ == "__main__":
    agent = DQNAgent()
    state_sample = np.random.rand(5)
    action = agent.act(state_sample)
    print(f"🧠 AI 선택: {'BUY' if action == 1 else 'SELL'}")

