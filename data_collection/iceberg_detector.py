import websocket
import json
import pandas as pd
import numpy as np
import time
import threading
import requests
import matplotlib.pyplot as plt
import os
from collections import deque
from dotenv import load_dotenv
from coin_selector import SELECTED_COIN  # 📌 `coin_selector.py`에서 코인 선택 변수 가져오기

# 환경 변수 로드 (.env 파일에서 API 키 및 Telegram 설정 가져오기)
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BINANCE_WS_URL = os.getenv("BINANCE_WS_URL", "wss://fstream.binance.com/ws/")

class IcebergDetector:
    def __init__(self, depths=[100], threshold=0.6, window_size=10):
        self.symbol = SELECTED_COIN  # ✅ `coin_selector.py`에서 선택된 코인 적용
        self.depths = depths
        self.threshold = threshold  # Iceberg 주문 탐지 민감도 (0~1)
        self.window_size = window_size  # 최근 몇 개의 주문을 비교할지
        self.recent_orders = []  # 최근 주문 저장
        self.price_levels = deque(maxlen=100)  # Iceberg 감지된 가격대 저장
        self.order_sizes = deque(maxlen=100)  # Iceberg 주문량 저장

        # ✅ `coin_selector.py`에서 가져온 코인으로 WebSocket URL 설정
        self.ws_url = f"{BINANCE_WS_URL}{self.symbol.lower()}@depth@100ms"

        # 차트 초기화 (OBS 시각화 지원)
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 5))

    def send_telegram_alert(self, message):
        """ Iceberg 주문 감지 시 Telegram 알림 전송 """
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.post(url, data=payload)
        else:
            print("⚠️ Telegram 설정이 누락되었습니다! .env 파일을 확인하세요.")

    def detect_iceberg_order(self, data):
        """ Iceberg 주문 감지 """
        orders = np.array([[float(price), float(size)] for price, size in data["bids"] + data["asks"]])

        if len(self.recent_orders) < self.window_size:
            self.recent_orders.append(orders)
            return None  # 충분한 데이터가 없으면 분석 X

        previous_orders = self.recent_orders.pop(0)  # 가장 오래된 데이터 제거
        self.recent_orders.append(orders)  # 최신 데이터 추가

        # 가격대별 주문량 변화율 계산
        delta_orders = orders[:, 1] - previous_orders[:, 1]
        iceberg_candidates = delta_orders[delta_orders < 0]  # 감소한 주문 탐색

        if iceberg_candidates.size > 0:
            iceberg_ratio = abs(np.mean(iceberg_candidates) / np.mean(orders[:, 1]))
            if iceberg_ratio > self.threshold:
                iceberg_price = np.mean(orders[:, 0])  # Iceberg 주문이 감지된 가격대
                iceberg_size = abs(np.sum(iceberg_candidates))  # Iceberg 주문 총량

                # 감지된 가격대 및 주문량 기록
                self.price_levels.append(iceberg_price)
                self.order_sizes.append(iceberg_size)

                print(f"🚨 [Iceberg 주문 감지] {time.strftime('%H:%M:%S')} | 가격대: {iceberg_price} | 주문량: {iceberg_size}")

                # Telegram 알림 전송
                self.send_telegram_alert(f"📊 [Iceberg 주문 감지] {self.symbol.upper()}\n"
                                         f"🕒 시간: {time.strftime('%H:%M:%S')}\n"
                                         f"💰 가격대: {iceberg_price}\n"
                                         f"📈 주문량: {iceberg_size}")

                # 차트 업데이트
                self.update_chart()
                return True
        return False

    def process_order_book(self, data):
        """ WebSocket을 통해 수신된 주문장 데이터 처리 """
        iceberg_detected = self.detect_iceberg_order(data)
        if iceberg_detected:
            print(f"📊 [경고] {self.symbol.upper()} Iceberg 주문 발생")

    def update_chart(self):
        """ Iceberg 주문 실시간 시각화 (OBS 연동) """
        self.ax.clear()
        self.ax.scatter(self.price_levels, self.order_sizes, label="Iceberg Orders", color="red", marker="o", alpha=0.7)
        self.ax.set_title(f"Iceberg Orders ({self.symbol.upper()})")
        self.ax.set_xlabel("Price Level")
        self.ax.set_ylabel("Order Size")
        self.ax.legend()
        plt.draw()
        plt.pause(0.01)

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 후 처리 """
        data = json.loads(message)
        self.process_order_book(data)

    def run(self):
        """ WebSocket 실행 """
        ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_message)
        print(f"🟢 {self.symbol} Iceberg 주문 감지 시작")
        ws.run_forever()

    def start_analysis(self):
        """ 백그라운드 스레드에서 분석 시작 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    iceberg_detector = IcebergDetector()
    iceberg_detector.start_analysis()

    time.sleep(60)
    print("✅ Iceberg 주문 감지 종료")
