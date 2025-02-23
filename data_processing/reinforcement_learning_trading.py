import gym
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from data_processing.time_series_analysis import get_time_series_data
from ai_prediction import predict_price  # AI 예측 가격 가져오기

# 🔥 1. 트레이딩 환경 정의
class TradingEnv(gym.Env):
    def __init__(self, selected_coins=SELECTED_COINS, initial_balance=10000):
        super(TradingEnv, self).__init__()
        self.selected_coins = selected_coins
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0  # 현재 포지션
        self.current_step = 0

        # 상태(State) 공간: 각 코인의 가격, 호가창 데이터, 거래량, 변동성 등
        self.data = {symbol: get_time_series_data(symbol) for symbol in selected_coins}
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(len(self.data[self.selected_coins[0]][0]),), dtype=np.float32
        )

        # 행동(Action) 공간: 매수, 매도, 유지
        self.action_space = gym.spaces.Discrete(3)

    def step(self, action):
        done = False
        reward = 0
        prev_price = self.data[self.selected_coins[0]][self.current_step]
        self.current_step += 1
        current_price = self.data[self.selected_coins[0]][self.current_step]

        if action == 1:  # 매수 (Buy)
            self.position = 1
            self.balance -= current_price
        elif action == 2:  # 매도 (Sell)
            self.position = -1
            self.balance += current_price

        # 수익 계산
        reward = (current_price - prev_price) * self.position
        if self.balance <= 0:
            done = True  # 잔고가 0 이하로 떨어지면 종료

        # 상태 갱신
        state = np.array(self.data[self.selected_coins[0]][self.current_step])

        return state, reward, done, {}

    def reset(self):
        self.balance = self.initial_balance
        self.position = 0
        self.current_step = 0
        return np.array(self.data[self.selected_coins[0]][self.current_step])

# 🔥 2. PPO 알고리즘 적용
def train_model():
    env = DummyVecEnv([lambda: TradingEnv()])  # 벡터화된 환경 생성
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.001, n_steps=512, batch_size=64)
    model.learn(total_timesteps=10000)

    # 모델 저장
    model.save("ppo_trading_model")
    print("🚀 PPO 모델 학습 완료!")

    return model

# 🔥 3. 모델 평가
def evaluate_model(model, env):
    obs = env.reset()
    total_reward = 0
    done = False

    while not done:
        action, _states = model.predict(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward

    print(f"총 보상: {total_reward}")

# ✅ 사용 예시
if __name__ == "__main__":
    # PPO 모델 학습
    model = train_model()

    # 학습된 모델 평가
    test_env = TradingEnv(selected_coins=["BTCUSDT", "ETHUSDT"])
    evaluate_model(model, test_env)
