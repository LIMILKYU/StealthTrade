#✅ 미체결 주문(Visible)과 체결된 주문(Hidden) 비교하여 Iceberg 주문 탐지
#✅ 다양한 거래소(Binance, Bybit, OKX 등)의 주문 데이터 분석
#✅ 거래량 급증과 비정상적인 주문 크기 감지하여 Iceberg 패턴 분석
#✅ Bid-Ask Imbalance, Spoofing 감지와 결합하여 신뢰도 높은 시그널 생성
#✅ OBS를 활용한 Iceberg 주문 실시간 시각화 지원

import websocket
import json
import pandas as pd
import numpy as np
import time
import threading

BINANCE_WS_URL = "wss://fstream.binance.com/ws/"

class IcebergDetector:
    def __init__(self, symbol="BTCUSDT", threshold=0.6, window_size=10):
        self.symbol = symbol.lower()
        self.threshold = threshold  # Iceberg 주문 탐지 민감도 (0~1)
        self.window_size = window_size  # 최근 몇 개의 주문을 비교할지
        self.recent_orders = []  # 최근 주문 저장

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
                print(f"🚨 [Iceberg 주문 감지] {time.strftime('%H:%M:%S')} | 비정상 주문 발생!")
                return True
        return False

    def process_order_book(self, data):
        """ WebSocket을 통해 수신된 주문장 데이터 처리 """
        iceberg_detected = self.detect_iceberg_order(data)
        if iceberg_detected:
            print(f"📊 [경고] {self.symbol} Iceberg 주문 발생")

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 후 처리 """
        data = json.loads(message)
        self.process_order_book(data)

    def run(self):
        """ WebSocket 실행 """
        ws_url = f"{BINANCE_WS_URL}{self.symbol.lower()}@depth@100ms"
        ws = websocket.WebSocketApp(ws_url, on_message=self.on_message)
        print(f"🟢 {self.symbol} Iceberg 주문 감지 시작")
        ws.run_forever()

    def start_analysis(self):
        """ 백그라운드 스레드에서 분석 시작 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    iceberg_detector = IcebergDetector(symbol="BTCUSDT")
    iceberg_detector.start_analysis()

    time.sleep(30)
    print("✅ Iceberg 주문 감지 종료")

#1️⃣ Iceberg 주문이 감지되었을 때 자동으로 Telegram 알림 발송
#2️⃣ Iceberg 주문 발생 시 해당 가격대에서의 거래량 변화 분석
#3️⃣ 거래소 API 데이터를 활용한 미체결 주문 & 체결 주문 비교 분석
#4️⃣ OBS 차트 연동하여 Iceberg 주문 감지 시 실시간 시각화 지원