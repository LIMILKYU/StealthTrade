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

class MarketDepthAnalyzer:
    def __init__(self, depth_levels=[5, 10, 20, 50, 100], timeframes=["1s", "5s", "1m", "5m"]):
        self.symbol = SELECTED_COIN  # ✅ `coin_selector.py`에서 선택된 코인 적용
        self.depth_levels = depth_levels
        self.timeframes = timeframes
        self.order_book_data = {tf: deque(maxlen=300) for tf in self.timeframes}  # ✅ 최근 5분(300초) 데이터 저장
        self.recent_depth = None  # ✅ 최신 Depth 데이터 저장

        # ✅ `coin_selector.py`에서 가져온 코인으로 WebSocket URL 설정
        self.ws_url = f"{BINANCE_WS_URL}{self.symbol.lower()}@depth@100ms"

        # 차트 초기화 (OBS 시각화 지원)
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 5))

    def calculate_depth_metrics(self, data):
        """ 시장 깊이 분석 및 유동성 평가 """
        bids = np.array([[float(price), float(size)] for price, size in data["bids"]])
        asks = np.array([[float(price), float(size)] for price, size in data["asks"]])

        depth_summary = {}

        for depth in self.depth_levels:
            bid_total = np.sum(bids[:depth, 1])  # Depth 범위 내 매수 총량
            ask_total = np.sum(asks[:depth, 1])  # Depth 범위 내 매도 총량
            bid_ask_ratio = bid_total / (ask_total + 1e-9)  # Bid-Ask 비율 (0으로 나누기 방지)
            depth_summary[f"Depth{depth}_Bid_Ask_Ratio"] = bid_ask_ratio

        return depth_summary

    def update_order_book_history(self, depth_data):
        """ 다양한 시간 프레임에서 호가창 데이터를 저장 """
        current_time = time.time()
        for timeframe in self.timeframes:
            self.order_book_data[timeframe].append((current_time, depth_data))

    def process_order_book(self, data):
        """ WebSocket을 통해 수신된 호가창 데이터 처리 """
        depth_metrics = self.calculate_depth_metrics(data)
        self.recent_depth = depth_metrics  # 최신 데이터 업데이트
        self.update_order_book_history(depth_metrics)

        print(f"📊 [시장 깊이 분석] {self.symbol} | {depth_metrics}")

        # ✅ 차트 업데이트 (OBS 연동)
        self.update_chart()

    def send_telegram_alert(self, message):
        """ Telegram 알림 전송 """
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.post(url, data=payload)
        else:
            print("⚠️ Telegram 설정이 누락되었습니다! .env 파일을 확인하세요.")

    def update_chart(self):
        """ 시장 깊이 변화를 실시간 시각화 (OBS 연동) """
        self.ax.clear()

        # 최근 100개 데이터 기준으로 시각화
        if len(self.order_book_data["1s"]) > 1:
            times = [time.strftime('%H:%M:%S', time.localtime(t[0])) for t in self.order_book_data["1s"]]
            depth_values = [t[1]["Depth100_Bid_Ask_Ratio"] for t in self.order_book_data["1s"]]

            self.ax.plot(times, depth_values, label="Depth100 Bid-Ask Ratio", color="blue")

        self.ax.set_title(f"Market Depth Analysis ({self.symbol.upper()})")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Bid-Ask Ratio")
        self.ax.legend()
        plt.xticks(rotation=45)
        plt.draw()
        plt.pause(0.01)

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 후 처리 """
        data = json.loads(message)
        self.process_order_book(data)

    def run(self):
        """ WebSocket 실행 """
        ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_message)
        print(f"🟢 {self.symbol} 시장 깊이 분석 시작")
        ws.run_forever()

    def start_analysis(self):
        """ 백그라운드 스레드에서 분석 시작 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    market_depth_analyzer = MarketDepthAnalyzer()
    market_depth_analyzer.start_analysis()

    time.sleep(60)
    print("✅ 시장 깊이 분석 종료")
