import websocket
import json
import numpy as np
import requests
import os
import logging
import time
import matplotlib.pyplot as plt
from collections import deque
from dotenv import load_dotenv
from pymongo import MongoClient

# ✅ 환경 변수 로드
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BINANCE_WS_URL = os.getenv("BINANCE_WS_URL", "wss://fstream.binance.com/ws/")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "trading_data")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "iceberg_orders")

class IcebergDetector:
    def __init__(self, symbol="BTCUSDT", threshold=0.6, window_size=10):
        """ ✅ Iceberg 주문 탐지 클래스 """
        self.symbol = symbol.upper()
        self.threshold = threshold  # Iceberg 주문 탐지 민감도 (0~1)
        self.window_size = window_size  # 최근 몇 개의 주문을 비교할지
        self.recent_orders = deque(maxlen=self.window_size)
        self.mongo_client = MongoClient(MONGO_URL)
        self.db = self.mongo_client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION]

        # ✅ WebSocket URL 설정
        self.ws_url = f"{BINANCE_WS_URL}{self.symbol.lower()}@depth@100ms"

        # 차트 초기화 (OBS 시각화 지원)
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 5))

    def send_telegram_alert(self, message):
        """ ✅ Iceberg 주문 감지 시 Telegram 알림 전송 """
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.post(url, data=payload)
        else:
            logging.warning("⚠️ Telegram 설정이 누락되었습니다! .env 파일을 확인하세요.")

    def detect_iceberg_order(self, data):
        """ ✅ Iceberg 주문 탐지 """
        orders = np.array([[float(price), float(size)] for price, size in data["bids"] + data["asks"]])

        if len(self.recent_orders) < self.window_size:
            self.recent_orders.append(orders)
            return None  # 충분한 데이터가 쌓일 때까지 대기

        prev_orders = self.recent_orders.popleft()
        self.recent_orders.append(orders)

        # ✅ 주문량 변화 감지 (Bid-Ask Imbalance + Iceberg 주문 패턴 분석)
        price_diffs = np.abs(prev_orders[:, 0] - orders[:, 0])
        size_diffs = np.abs(prev_orders[:, 1] - orders[:, 1])
        large_orders = size_diffs > (np.mean(size_diffs) * self.threshold)

        if np.any(large_orders):
            iceberg_price = orders[large_orders, 0]
            iceberg_size = orders[large_orders, 1]
            result = {"timestamp": time.time(), "symbol": self.symbol, "price": iceberg_price.tolist(), "size": iceberg_size.tolist()}

            # ✅ 데이터 저장 (MongoDB)
            self.collection.insert_one(result)
            logging.info(f"✅ [Iceberg 주문 감지] {result}")

            # ✅ Telegram 알림 전송
            self.send_telegram_alert(f"🚨 Iceberg 주문 감지! 가격: {iceberg_price.tolist()}, 수량: {iceberg_size.tolist()}")

            # ✅ 차트 업데이트
            self.ax.clear()
            self.ax.scatter(iceberg_price, iceberg_size, color="red", label="Iceberg 주문")
            self.ax.set_title(f"Iceberg 주문 감지 - {self.symbol}")
            self.ax.legend()
            plt.draw()
            plt.pause(0.1)

    def on_message(self, ws, message):
        """ ✅ WebSocket 메시지 처리 (호가 데이터 수신) """
        data = json.loads(message)
        self.detect_iceberg_order(data)

    def on_error(self, ws, error):
        logging.error(f"🚨 WebSocket 오류 발생: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logging.warning(f"⚠️ WebSocket 연결 종료! 5초 후 재연결...")
        time.sleep(5)
        self.start_websocket()  # ✅ 자동 재연결 기능 추가

    def start_websocket(self):
        """ ✅ WebSocket 연결 시작 (자동 재연결 포함) """
        ws = websocket.WebSocketApp(self.ws_url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.run_forever()

# ✅ 사용 예시
if __name__ == "__main__":
    detector = IcebergDetector("BTCUSDT")
    detector.start_websocket()
