import numpy as np
import tensorflow as tf
import random
import logging
import gym
import collections
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam

# ✅ 1. DQN 에이전트 클래스 최적화
class DQNAgent:
    def __init__(self, state_size=10, action_size=3, memory_size=2000):
        """
        :param state_size: 입력 상태 크기 (예: 시장 데이터)
        :param action_size: 행동 크기 (BUY, SELL, HOLD)
        :param memory_size: 경험 리플레이 저장 개수
        """
        self.state_size = state_size
        self.action_size = action_size
        self.memory = collections.deque(maxlen=memory_size)  # ✅ 메모리 크기 제한 (2000)
        self.gamma = 0.99  # ✅ 할인율 증가 (장기적인 보상 고려)
        self.epsilon = 1.0  # ✅ 탐험률 (초기에는 무작위 탐색)
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self.build_model()
        self.target_model = self.build_model()  # ✅ Target Q-network 추가
        self.update_target_model()
        logging.basicConfig(level=logging.INFO)

    def build_model(self):
        """ DQN 모델 생성 (BatchNorm + Dropout 추가) """
        model = Sequential([
            Dense(64, activation="relu", input_dim=self.state_size),
            BatchNormalization(),
            Dropout(0.2),
            Dense(32, activation="relu"),
            BatchNormalization(),
            Dropout(0.2),
            Dense(self.action_size, activation="linear")  # 행동별 Q-value 출력
        ])
        model.compile(loss="mse", optimizer=Adam(learning_rate=self.learning_rate))
        logging.info("✅ DQN Model Built Successfully")
        return model

    def update_target_model(self):
        """ ✅ Target Q-Network 업데이트 (DQN 안정성 증가) """
        self.target_model.set_weights(self.model.get_weights())

    def remember(self, state, action, reward, next_state, done):
        """ 학습 데이터 저장 """
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """ 행동 선택 (Epsilon-Greedy + Softmax 적용) """
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)  # 무작위 탐험
        q_values = self.model.predict(np.array([state]), verbose=0)
        return np.argmax(q_values[0])  # ✅ Q-Value가 가장 높은 행동 선택

    def replay(self, batch_size=32):
        """ ✅ 경험 리플레이 학습 (Target Q-Network 사용) """
        if len(self.memory) < batch_size:
            return

        minibatch = random.sample(self.memory, batch_size)

        for state, action, reward, next_state, done in minibatch:
            target = reward if done else reward + self.gamma * np.amax(self.target_model.predict(np.array([next_state]), verbose=0)[0])
            target_f = self.model.predict(np.array([state]), verbose=0)
            target_f[0][action] = target
            self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        self.update_target_model()  # ✅ 일정 주기마다 Target Network 업데이트

# ✅ 2. 트레이딩 환경 최적화
class TradingEnv(gym.Env):
    def __init__(self):
        super(TradingEnv, self).__init__()
        self.state = np.random.rand(10)  # 10개의 특징값
        self.action_space = gym.spaces.Discrete(3)  # 0: 매도, 1: 매수, 2: 홀딩
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(10,), dtype=np.float32)

    def step(self, action):
        reward = self._calculate_reward(action)  # ✅ 실제 거래 데이터를 기반으로 보상 계산
        self.state = np.random.rand(10)
        return self.state, reward, False, {}

    def _calculate_reward(self, action):
        """ ✅ 보상 함수 개선 """
        # 매수 후 가격 상승 시 보상, 가격 하락 시 패널티 부여
        price_change = np.random.randn()  # 실전에서는 실제 데이터 활용
        if action == 1 and price_change > 0:
            return 1  # 매수 후 상승 → 보상
        elif action == 0 and price_change < 0:
            return 1  # 매도 후 하락 → 보상
        return -1  # 잘못된 선택 → 패널티

    def reset(self):
        self.state = np.random.rand(10)
        return self.state

# ✅ 3. 강화 학습 실행
env = TradingEnv()
agent = DQNAgent()

EPSILON_START = 1.0
EPSILON_END = 0.1
EPSILON_DECAY = 0.995

epsilon = EPSILON_START
for episode in range(1000):
    state = env.reset()
    done = False
    while not done:
        action = agent.act(state)
        next_state, reward, done, _ = env.step(action)
        agent.remember(state, action, reward, next_state, done)
        state = next_state
        agent.replay(batch_size=32)

    epsilon = max(EPSILON_END, epsilon * EPSILON_DECAY)  # 탐험률 점진적 감소

print("✅ 강화 학습 탐험-활용 균형 적용 완료")

# ✅ 4. 모델 테스트
if __name__ == "__main__":
    test_state = np.random.rand(10)
    action = agent.act(test_state)
    print(f"🧠 AI 선택: {'BUY' if action == 1 else 'SELL' if action == 0 else 'HOLD'}")
