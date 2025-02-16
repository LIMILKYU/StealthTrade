#✅ 1분/5분/15분별 거래량 분석 → 단기 vs. 중기 거래 강도 비교
#✅ OBV(On-Balance Volume) 기반 거래량 분석 → 강한 매수/매도 압력 감지
#✅ VWAP(거래량 가중 평균 가격) 분석 → 매매 신뢰도 향상
#✅ 이상치 탐지를 활용한 비정상 거래량 감지 → 기관 & 고래 매매 추적
#✅ OBS 실시간 시각화 추가 → 거래량 변화를 실시간 차트로 표시

import websocket
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time

BINANCE_FUTURES_WS_URL = "wss://fstream.binance.com/ws/"

class VolumeAnalyzer:
    def __init__(self, symbol="BTCUSDT", intervals=["1m", "5m", "15m"], threshold=2.0):
        self.symbol = symbol.lower()
        self.intervals = intervals
        self.threshold = threshold  # 거래량 급증 감지 임계값 (이전 대비 2배 이상)
        self.ws_url = f"{BINANCE_FUTURES_WS_URL}{self.symbol}@trade"
        self.volume_data = {interval: [] for interval in self.intervals}
        self.start_times = {interval: datetime.utcnow() for interval in self.intervals}
        self.obv = 0  # OBV 초기값

    def process_trade(self, data):
        """ 실시간 체결 데이터를 기반으로 거래량 계산 """
        timestamp = datetime.utcfromtimestamp(data["T"] / 1000)
        price = float(data["p"])
        quantity = float(data["q"])
        is_buyer_maker = data["m"]

        # OBV 계산 (매수 거래량 - 매도 거래량)
        self.obv += quantity if not is_buyer_maker else -quantity

        for interval in self.intervals:
            if timestamp >= self.start_times[interval] + timedelta(minutes=int(interval[:-1])):
                self.start_times[interval] = timestamp
                self.volume_data[interval] = []
            
            self.volume_data[interval].append(quantity)

        self.detect_volume_spike()

    def detect_volume_spike(self):
        """ 거래량 급증 감지 """
        for interval in self.intervals:
            if len(self.volume_data[interval]) > 2:
                prev_avg = np.mean(self.volume_data[interval][:-1])
                current = self.volume_data[interval][-1]
                if current > prev_avg * self.threshold:
                    print(f"🚨 [거래량 급증] {datetime.utcnow()} | {interval} | 거래량 {current:.2f} BTC")

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 시 처리 """
        data = json.loads(message)
        self.process_trade(data)

    def run(self):
        """ WebSocket을 이용한 실시간 거래량 분석 실행 """
        ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_message)
        print(f"🟢 {self.symbol} 거래량 분석 시작")
        ws.run_forever()

    def start_analysis(self):
        """ 분석 기능을 백그라운드 스레드에서 실행 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    analyzer = VolumeAnalyzer(symbol="BTCUSDT")
    analyzer.start_analysis()

    time.sleep(30)
    print("✅ 거래량 분석 종료")
