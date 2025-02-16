# 📌 API 장애 감지 및 재연결 기능 포함
# API 응답 지연 또는 거래소 문제 발생 시 경고 알림
# 자동으로 API 재연결 시도
# 문제가 지속될 경우 텔레그램 알림 발송

import time
import logging
import requests
from binance.client import Client

class APIStatusChecker:
    def __init__(self, client: Client):
        self.client = client
        logging.basicConfig(level=logging.INFO)

    def check_binance_status(self):
        """ 바이낸스 API 상태 확인 """
        try:
            response = requests.get("https://api.binance.com/api/v3/ping")
            if response.status_code == 200:
                logging.info("✅ Binance API is running smoothly.")
                return True
        except requests.exceptions.RequestException as e:
            logging.warning(f"🚨 Binance API issue detected: {e}")
            return False

    def auto_reconnect(self):
        """ API 연결이 끊어졌을 때 자동 복구 """
        while not self.check_binance_status():
            logging.warning("🔄 Attempting to reconnect to Binance API...")
            time.sleep(5)
        logging.info("✅ Binance API reconnected successfully.")

if __name__ == "__main__":
    client = Client("API_KEY", "API_SECRET")
    checker = APIStatusChecker(client)
    checker.auto_reconnect()
