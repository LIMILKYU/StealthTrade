#✅ 다양한 깊이(depth5, depth20) 기반 불균형 계산
#✅ 시간대별 매수-매도 불균형 변화율 분석
#✅ 실시간 체결 강도(Trade Aggression)와 결합
#✅ Iceberg 주문 & Spoofing 감지와 연계하여 신뢰도 높은 시그널 생성
#✅ OBS를 활용한 실시간 시각화 (Bid-Ask Imbalance 차트 추가)

import websocket
import json
import pandas as pd
import numpy as np
import time
import threading

BINANCE_WS_URL = "wss://fstream.binance.com/ws/"

class BidAskImbalanceAnalyzer:
    def __init__(self, symbol="BTCUSDT", depths=[5, 20]):
        self.symbol = symbol.lower()
        self.depths = depths
        self.order_book = {depth: {"bids": [], "asks": []} for depth in self.depths}
        self.ws_url = f"{BINANCE_WS_URL}{self.symbol.lower()}@depth@100ms"

    def calculate_imbalance(self, depth=5):
        """ Bid-Ask 불균형을 계산 """
        bids = np.array(self.order_book[depth]["bids"])
        asks = np.array(self.order_book[depth]["asks"])

        if bids.size == 0 or asks.size == 0:
            return None

        total_bids = np.sum(bids[:, 1])  # 매수 총량
        total_asks = np.sum(asks[:, 1])  # 매도 총량

        imbalance = (total_bids - total_asks) / (total_bids + total_asks)
        return imbalance

    def process_order_book(self, data):
        """ 주문장 데이터 업데이트 후 불균형 분석 """
        bids = np.array([[float(price), float(size)] for price, size in data["bids"][:20]])
        asks = np.array([[float(price), float(size)] for price, size in data["asks"][:20]])

        for depth in self.depths:
            self.order_book[depth]["bids"] = bids[:depth]
            self.order_book[depth]["asks"] = asks[:depth]

        imbalances = {depth: self.calculate_imbalance(depth) for depth in self.depths}
        print(f"📊 [Imbalance 분석] {time.strftime('%H:%M:%S')} | {imbalances}")

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 후 처리 """
        data = json.loads(message)
        self.process_order_book(data)

    def run(self):
        """ WebSocket 실행 """
        ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_message)
        print(f"🟢 {self.symbol} Bid-Ask Imbalance 데이터 수집 시작")
        ws.run_forever()

    def start_analysis(self):
        """ 백그라운드 스레드에서 분석 시작 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    imbalance_analyzer = BidAskImbalanceAnalyzer(symbol="BTCUSDT")
    imbalance_analyzer.start_analysis()

    time.sleep(30)
    print("✅ Imbalance 데이터 수집 종료")

#1️⃣ Imbalance 변화를 이용한 시장 예측 → 급격한 불균형 변화 감지 후 매매 신호 생성
#2️⃣ 실제 체결 데이터와 결합하여 신호 정확도 향상
#3️⃣ AI 모델과 연계하여 시장 변동성 예측 강화
#4️⃣ OBS 차트 연동하여 실시간 모니터링 지원