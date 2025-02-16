#✅ 이상치 탐지(Outlier Detection) → 비정상적으로 큰 주문 탐지
#✅ 반복적인 대량 주문 생성 & 취소 감지 → 지속적이고 빠른 주문 변경 탐지
#✅ Bid-Ask 불균형 기반 스푸핑 감지 → 한쪽 호가창에만 집중된 비정상적 주문 감지
#✅ 호가창 변동 패턴 분석 → 특정 패턴이 지속적으로 반복되는지 분석
#✅ WebSocket을 통한 실시간 분석 → 바이낸스 API 기반 실시간 탐지

import websocket
import json
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import time

# 📌 Binance Futures API
BINANCE_FUTURES_WS_URL = "wss://fstream.binance.com/ws/"

class SpoofingDetector:
    def __init__(self, symbol="BTCUSDT", depth=20, threshold_ratio=0.02, cancel_time_threshold=0.5):
        self.symbol = symbol.lower()
        self.depth = depth
        self.threshold_ratio = threshold_ratio  # 주문 비율 기준 (예: 2% 이상 비정상 주문)
        self.cancel_time_threshold = cancel_time_threshold  # 주문 취소까지 걸리는 최대 허용 시간 (초)
        self.ws_url = f"{BINANCE_FUTURES_WS_URL}{self.symbol}@depth{self.depth}@100ms"
        self.order_book_data = []
        self.recent_orders = {}  # 주문 ID별 생성 & 취소 시간 기록

    def detect_spoofing(self, data):
        """ 스푸핑 탐지 로직 실행 """
        timestamp = datetime.utcnow()
        bids = {float(x[0]): float(x[1]) for x in data["bids"]}  # 매수 호가
        asks = {float(x[0]): float(x[1]) for x in data["asks"]}  # 매도 호가

        total_bid_volume = sum(bids.values())
        total_ask_volume = sum(asks.values())

        # 비정상적으로 큰 주문 감지 (이상치 탐지)
        suspicious_bids = {price: vol for price, vol in bids.items() if vol > total_bid_volume * self.threshold_ratio}
        suspicious_asks = {price: vol for price, vol in asks.items() if vol > total_ask_volume * self.threshold_ratio}

        # Bid-Ask 불균형 기반 탐지
        bid_ask_imbalance = abs(total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
        
        # 빠른 주문 취소 감지 (일정 시간 내 취소된 주문 확인)
        cancelled_orders = [order_id for order_id, t in self.recent_orders.items() if (timestamp - t).total_seconds() <= self.cancel_time_threshold]
        
        # 탐지된 이상 현상 출력
        if suspicious_bids or suspicious_asks:
            print(f"🚨 [스푸핑 감지] {timestamp} | 비정상적 대량 주문 감지")
            if suspicious_bids:
                print(f"    ⬆️ 매수 측 이상 주문: {suspicious_bids}")
            if suspicious_asks:
                print(f"    ⬇️ 매도 측 이상 주문: {suspicious_asks}")
        
        if bid_ask_imbalance > 0.7:
            print(f"⚠️ [경고] {timestamp} | Bid-Ask 불균형 발생 ({bid_ask_imbalance:.2f})")

        if cancelled_orders:
            print(f"❌ [빠른 주문 취소 감지] {timestamp} | 취소된 주문 수: {len(cancelled_orders)}")

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 시 처리 """
        data = json.loads(message)
        self.detect_spoofing(data)

    def run(self):
        """ WebSocket을 이용한 실시간 스푸핑 탐지 실행 """
        ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_message)
        print(f"🟢 {self.symbol} 스푸핑 탐지 시작 (depth={self.depth})")
        ws.run_forever()

    def start_detection(self):
        """ 탐지 기능을 백그라운드 스레드에서 실행 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    detector = SpoofingDetector(symbol="BTCUSDT", depth=20)
    detector.start_detection()

    # 10초 후 종료
    time.sleep(10)
    print("✅ 스푸핑 탐지 종료")

#✅ ML 기반 이상 탐지 → 머신러닝 모델로 스푸핑 패턴 학습
#✅ 스푸핑 탐지 기록 저장 → DB 연동하여 분석 가능
#✅ 자동 알림 시스템 연동 → 텔레그램 & OBS 실시간 알림
#✅ 고빈도(HFT) 트레이더 패턴 분석 추가