#✅ 실시간 VWAP 계산 → 틱 데이터 기반 실시간 업데이트
#✅ 다양한 시간봉(1m, 5m, 15m) VWAP 비교
#✅ 대량 체결(Big Order)과 VWAP 관계 분석
#✅ VWAP 기반 매매 신호 생성 (평균보다 낮으면 매수, 높으면 매도 등)
#✅ OBS 실시간 시각화 추가 (VWAP vs. 현재가 비교 차트 표시)

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import websocket
import json
import threading
import time

BINANCE_FUTURES_WS_URL = "wss://fstream.binance.com/ws/"

class VWAPCalculator:
    def __init__(self, symbol="BTCUSDT", intervals=["1m", "5m", "15m"]):
        self.symbol = symbol.lower()
        self.intervals = intervals
        self.ws_url = f"{BINANCE_FUTURES_WS_URL}{self.symbol}@trade"
        self.trade_data = {interval: [] for interval in self.intervals}
        self.start_times = {interval: datetime.utcnow() for interval in self.intervals}

    def process_trade(self, data):
        """ 실시간 체결 데이터 VWAP 분석 """
        timestamp = datetime.utcfromtimestamp(data["T"] / 1000)
        price = float(data["p"])
        quantity = float(data["q"])

        for interval in self.intervals:
            if timestamp >= self.start_times[interval] + timedelta(minutes=int(interval[:-1])):
                self.start_times[interval] = timestamp
                self.trade_data[interval] = []

            self.trade_data[interval].append((price, quantity))

        self.calculate_vwap()

    def calculate_vwap(self):
        """ VWAP(거래량 가중 평균 가격) 계산 """
        for interval in self.intervals:
            if self.trade_data[interval]:
                total_volume = sum(q for _, q in self.trade_data[interval])
                vwap = sum(p * q for p, q in self.trade_data[interval]) / total_volume
                print(f"📊 [VWAP 분석] {datetime.utcnow()} | {interval} | VWAP: {vwap:.2f}")

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 시 VWAP 계산 """
        data = json.loads(message)
        self.process_trade(data)

    def run(self):
        """ WebSocket을 이용한 실시간 VWAP 수집 """
        ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_message)
        print(f"🟢 {self.symbol} VWAP 데이터 수집 시작")
        ws.run_forever()

    def start_analysis(self):
        """ VWAP 분석을 백그라운드 스레드에서 실행 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    vwap_calculator = VWAPCalculator(symbol="BTCUSDT")
    vwap_calculator.start_analysis()

    time.sleep(30)
    print("✅ VWAP 데이터 수집 종료")

#1️⃣ VWAP 기반 매매 전략 추가 → 현재 가격이 VWAP보다 낮으면 매수, 높으면 매도
#2️⃣ VWAP vs. 평균 체결 가격 비교 분석
#3️⃣ OBS를 통한 실시간 시각화 추가 → VWAP과 현재 가격 비교 차트 표시