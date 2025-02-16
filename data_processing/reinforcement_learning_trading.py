# 🚀 PPO(정책 최적화) 기반의 강화학습 트레이딩 에이전트
# ✅ 강화학습 트레이딩 시스템 주요 기능
# ✔ PPO 알고리즘 적용: 안정적이고 강력한 자동매매 수행
# ✔ 실시간 시장 데이터 학습: 가격, 변동성, 거래량, 뉴스 감성 반영
# ✔ 최적의 매매 전략 학습: 강화학습 기반 자동매매 최적화
# ✔ AI가 스스로 전략 조정: 시장 변화에 따라 유연하게 대응
# ✔ 탐색(Exploration)과 활용(Exploitation) 전략 최적화

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
    def __init__(self):
        super(TradingEnv, self).__init__()
        self.ai_predicted_price = predict_price(LSTM_Predictor().cuda(), "price_data.csv")  # AI 가격 예측

    def step(self, action):
        # ✅ AI 예측 가격을 고려한 보상 함수
        reward = (self.current_price - self.ai_predicted_price) * self.position


class TradingEnv(gym.Env):
    def __init__(self, initial_balance=10000):
        super(TradingEnv, self).__init__()
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0  # 현재 포지션
        self.data = get_time_series_data()
        self.current_step = 0

        # 상태(State) 공간: 가격, 호가창 데이터, 거래량, 변동성 등
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(len(self.data[0]),), dtype=np.float32
        )

        # 행동(Action) 공간: 매수, 매도, 유지
        self.action_space = gym.spaces.Discrete(3)

    def step(self, action):
        done = False
        reward = 0
        prev_price = self.data[self.current_step]
        self.current_step += 1
        current_price = self.data[self.current_step]

        if action == 1:  # 매수 (Buy)
            self.position = 1
            self.balance -= current_price
        elif action == 2:  # 매도 (Sell)
            self.position = -1
            self.balance += current_price

        # 수익 계산
        reward = (current_price - prev_price) * self.position

        # 종료 조건
        if self.current_step >= len(self.data) - 1:
            done = True

        return self.data[self.current_step], reward, done, {}

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.position = 0
        return self.data[self.current_step]

# 🔥 2. 강화학습 모델 훈련
def train_agent():
    env = TradingEnv()
    env = DummyVecEnv([lambda: env])  # Stable-Baselines3 호환용
    model = PPO("MlpPolicy", env, verbose=1)
    
    print("🚀 강화학습 에이전트 훈련 시작...")
    model.learn(total_timesteps=50000)
    print("✅ 훈련 완료!")

    model.save("ppo_trading_agent")

# 🔥 3. 학습된 모델 테스트
def test_agent():
    model = PPO.load("ppo_trading_agent")
    env = TradingEnv()
    state = env.reset()
    done = False
    total_profit = 0

    while not done:
        action, _ = model.predict(state)
        state, reward, done, _ = env.step(action)
        total_profit += reward

    print(f"🎯 최종 수익: {total_profit}")

if __name__ == "__main__":
    train_agent()
    test_agent()

# 📌 💡 추가 개선 가능 항목 
# ✅ DDPG, SAC 등 다른 RL 알고리즘 실험
# ✅ 더 정교한 보상 함수 추가
# ✅ 거래량 기반 변동성 조정
# ✅ 장기 학습을 통한 최적의 트레이딩 전략 탐색