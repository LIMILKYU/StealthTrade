import websocket
import json
import pandas as pd
import numpy as np
import time
import threading
import matplotlib.pyplot as plt
from collections import deque
import requests
import os
from dotenv import load_dotenv
from coin_selector import CoinSelector  # 📌 coin_selector.py에서 코인 선택 모듈 가져오기

# 환경 변수 로드 (.env 파일에서 API 키 및 설정값 가져오기)
load_dotenv()

BINANCE_WS_URL = os.getenv("BINANCE_WS_URL", "wss://fstream.binance.com/ws/")

# 📌 최적의 코인 선택
selector = CoinSelector()
SELECTED_COIN = selector.fetch_top_volatile_coins(top_n=1)[0]  # 변동성 높은 코인 1개 선택
print(f"🎯 [선택된 코인]: {SELECTED_COIN}")

class BidAskImbalanceAnalyzer:
    def __init__(self, depths=[100]):
        self.symbol = SELECTED_COIN  # ✅ 선정된 코인을 사용
        self.depths = depths
        self.order_book = {depth: {"bids": [], "asks": []} for depth in self.depths}

        # ✅ 변동성이 높은 코인 적용 후 WebSocket URL 생성
        self.ws_url = f"{BINANCE_WS_URL}{self.symbol.lower()}@depth@100ms"

        # 데이터 저장용 (최근 100개 데이터 저장)
        self.imbalance_history = deque(maxlen=100)
        self.trade_volume = deque(maxlen=100)
        self.time_stamps = deque(maxlen=100)

        # 차트 초기화
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 5))

    def calculate_imbalance(self, depth=100):
        """ Bid-Ask 불균형을 계산 """
        bids = np.array(self.order_book[depth]["bids"])
        asks = np.array(self.order_book[depth]["asks"])

        if bids.size == 0 or asks.size == 0:
            return None

        total_bids = np.sum(bids[:, 1])  # 매수 총량
        total_asks = np.sum(asks[:, 1])  # 매도 총량

        imbalance = (total_bids - total_asks) / (total_bids + total_asks)
        return imbalance

    def detect_spoofing(self, depth=100):
        """ Spoofing 감지: 비정상적인 대량 주문 후 빠른 취소 패턴 분석 """
        bids = np.array(self.order_book[depth]["bids"])
        asks = np.array(self.order_book[depth]["asks"])

        if bids.size == 0 or asks.size == 0:
            return False

        top_bid_size = bids[0, 1]
        top_ask_size = asks[0, 1]

        if top_bid_size > np.median(bids[:, 1]) * 5 or top_ask_size > np.median(asks[:, 1]) * 5:
            return True  # Spoofing 가능성 높음
        
        return False

    def detect_iceberg_order(self, depth=100):
        """ Iceberg 주문 감지: 작은 수량으로 반복되는 주문 """
        bids = np.array(self.order_book[depth]["bids"])
        asks = np.array(self.order_book[depth]["asks"])

        if bids.size == 0 or asks.size == 0:
            return False

        small_orders = (bids[:, 1] < np.median(bids[:, 1]) * 0.5).sum() + \
                       (asks[:, 1] < np.median(asks[:, 1]) * 0.5).sum()

        if small_orders > len(bids) * 0.5:
            return True  
        
        return False

    def process_order_book(self, data):
        """ 주문장 데이터 업데이트 후 불균형 분석 """
        bids = np.array([[float(price), float(size)] for price, size in data["bids"][:100]])
        asks = np.array([[float(price), float(size)] for price, size in data["asks"][:100]])

        for depth in self.depths:
            self.order_book[depth]["bids"] = bids[:depth]
            self.order_book[depth]["asks"] = asks[:depth]

        imbalances = {depth: self.calculate_imbalance(depth) for depth in self.depths}

        # 불균형 변화율 저장
        self.imbalance_history.append(imbalances[100])
        self.time_stamps.append(time.strftime('%H:%M:%S'))

        # Spoofing & Iceberg 감지
        spoofing_detected = self.detect_spoofing(100)
        iceberg_detected = self.detect_iceberg_order(100)

        # 로그 출력
        print(f"📊 [{self.time_stamps[-1]}] | Imbalance: {imbalances}")
        if spoofing_detected:
            print("🚨 Spoofing 감지됨!")
        if iceberg_detected:
            print("🐋 Iceberg 주문 감지됨!")

        # 차트 업데이트
        self.update_chart()

    def update_chart(self):
        """ 실시간 차트 업데이트 (OBS 연동) """
        self.ax.clear()
        self.ax.plot(self.time_stamps, self.imbalance_history, label="Bid-Ask Imbalance (depth100)", color="blue")
        self.ax.set_title(f"Real-time Bid-Ask Imbalance ({self.symbol}, Depth 100)")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Imbalance")
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
        print(f"🟢 {self.symbol} Bid-Ask Imbalance 데이터 수집 시작 (Depth 100 적용)")
        ws.run_forever()

    def start_analysis(self):
        """ 백그라운드 스레드에서 분석 시작 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    imbalance_analyzer = BidAskImbalanceAnalyzer()
    imbalance_analyzer.start_analysis()

    time.sleep(30)
    print("✅ Imbalance 데이터 수집 종료")
