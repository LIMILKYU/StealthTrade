import time
import logging
import requests
import os
from dotenv import load_dotenv
import pandas as pd
from ai_optimization.ai_real_time_optimizer import AIRealTimeOptimizer
from backend.t_rpc_client import tRPCClient
from notification.telegram_notifier import TelegramNotifier

# 환경 변수 로드
load_dotenv()

class RealTimeMonitor:
    def __init__(self):
        """ 실시간 시장 감시 및 변동성 분석 클래스 """
        self.api_url = "https://api.binance.com/api/v3/ticker/24hr"
        self.ai_optimizer = AIRealTimeOptimizer()
        self.trpc_client = tRPCClient(os.getenv("TRPC_API_URL"))
        self.telegram_notifier = TelegramNotifier(
            os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
        )
        logging.basicConfig(level=logging.INFO)

    def get_market_volatility(self):
        """ 시장 변동성 감지 (ATR, 볼린저 밴드 기반) """
        try:
            response = requests.get(self.api_url)
            data = response.json()

            df = pd.DataFrame(data)
            df["price_change"] = df["priceChangePercent"].astype(float) / 100
            df["ATR"] = df["price_change"].rolling(10).std()
            df["bollinger_width"] = df["price_change"].rolling(20).std() * 2  # 볼린저 밴드 폭

            return df.iloc[-1]["ATR"], df.iloc[-1]["bollinger_width"]

        except Exception as e:
            logging.error(f"⚠️ 시장 변동성 계산 오류: {e}")
            return None, None

    def start_monitoring(self):
        """ 실시간 AI 트레이딩 성과 및 시장 변동 감시 """
        logging.info("🚀 Real-Time AI Trading Monitor Started")
        while True:
            optimized_signal = self.ai_optimizer.update_strategy()
            atr, bollinger_width = self.get_market_volatility()

            if atr and bollinger_width:
                logging.info(f"📊 AI 신호: {optimized_signal}, ATR: {atr:.5f}, 볼린저 밴드 폭: {bollinger_width:.5f}")

                if atr > 0.05:  # 변동성이 급격히 증가한 경우
                    self.telegram_notifier.send_message(
                        f"⚠️ 시장 변동성 증가 감지!\n"
                        f"📊 AI 신호: {optimized_signal}\n"
                        f"ATR: {atr:.5f}, 볼린저 밴드 폭: {bollinger_width:.5f}"
                    )

                # tRPC API를 통해 프론트엔드 업데이트
                self.trpc_client.update_trade_data({
                    "ATR": atr,
                    "bollinger_width": bollinger_width,
                    "ai_signal": optimized_signal
                })

            time.sleep(5)  # 5초마다 업데이트

# 사용 예시
if __name__ == "__main__":
    monitor = RealTimeMonitor()
    monitor.start_monitoring()
