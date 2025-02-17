import logging
import pandas as pd
import numpy as np
import requests
import os
from dotenv import load_dotenv
from ai_optimization.ai_model import LSTMAIModel
from ai_optimization.reinforcement_learning import DQNAgent
from ai_optimization.data_feed import DataFeed
from ai_optimization.strategy_feedback import StrategyFeedback
from backend.t_rpc_client import tRPCClient
from notification.telegram_notifier import TelegramNotifier

# 환경 변수 로드
load_dotenv()

class AIRealTimeOptimizer:
    def __init__(self):
        """ AI 기반 실시간 전략 최적화 시스템 """
        self.api_url = os.getenv("TRPC_API_URL")  # tRPC API URL
        self.data_feed = DataFeed(self.api_url)
        self.lstm_model = LSTMAIModel(input_shape=(50, 7))  # 데이터 포인트 추가
        self.rl_agent = DQNAgent(state_size=7, action_size=2)
        self.strategy_feedback = StrategyFeedback("logs/trade_history.log")
        self.telegram_notifier = TelegramNotifier(
            os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
        )
        self.trpc_client = tRPCClient(self.api_url)

        logging.basicConfig(level=logging.INFO)

    def update_strategy(self):
        """ 실시간 데이터를 기반으로 AI 전략 최적화 """
        try:
            df = self.data_feed.get_market_data()
            if df is None or df.empty:
                logging.warning("❌ 시장 데이터 없음! 전략 업데이트 불가")
                return

            # 데이터 가공 (시장 변동성, 체결 강도, 매수/매도 불균형 추가)
            df["volatility"] = df["price"].pct_change().rolling(10).std()
            df["bid_ask_imbalance"] = df["bid_volume"] - df["ask_volume"]
            df["trade_volume_change"] = df["trade_volume"].pct_change()

            # LSTM 모델 예측
            prediction = self.lstm_model.predict(df.iloc[-50:].values.reshape(1, 50, 7))
            signal = "BUY" if prediction[0] > 0.5 else "SELL"

            # 강화 학습 기반 AI 최적화 적용
            state = df.iloc[-1].values
            action = self.rl_agent.act(state)

            # 전략 업데이트 반영
            self.strategy_feedback.update_strategy(action, signal)

            # tRPC API를 통해 프론트엔드 업데이트
            self.trpc_client.update_trade_data({
                "ai_signal": signal,
                "rl_action": action,
                "volatility": df["volatility"].iloc[-1],
                "bid_ask_imbalance": df["bid_ask_imbalance"].iloc[-1],
            })

            # 텔레그램 알림 전송
            self.telegram_notifier.send_message(
                f"📊 **AI 전략 최적화 업데이트**\n"
                f"✅ 예측 신호: {signal}\n"
                f"🔹 강화 학습 액션: {action}\n"
                f"📈 시장 변동성: {df['volatility'].iloc[-1]:.5f}\n"
                f"📊 매수/매도 불균형: {df['bid_ask_imbalance'].iloc[-1]}"
            )

        except requests.exceptions.RequestException as e:
            logging.error(f"🚨 API 오류 발생: {e}")
        except Exception as e:
            logging.error(f"⚠️ 예기치 않은 오류 발생: {e}")

if __name__ == "__main__":
    optimizer = AIRealTimeOptimizer()
    optimizer.update_strategy()
