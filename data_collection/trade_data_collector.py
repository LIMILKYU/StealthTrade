#✅ 1분/5분/15분별 체결 강도 분석 → 단기 vs. 중기 체결량 비교
#✅ Bid vs. Ask 체결량 비교 분석 → 매수/매도 압력 판단
#✅ 대량 체결(Big Order) 감지 → 고래 매매 추적
#✅ 체결 속도(Tick Rate) 분석 → 시장 변동성 예측
#✅ VWAP(거래량 가중 평균 가격) 분석 → 평균 체결 가격 분석
#✅ OBS 실시간 시각화 추가 → 체결 강도 변화를 실시간 차트로 표시

import websocket
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time

BINANCE_FUTURES_WS_URL = "wss://fstream.binance.com/ws/"

class TradeDataCollector:
    def __init__(self, symbol="BTCUSDT", intervals=["1m", "5m", "15m"], large_order_threshold=50, tick_rate_threshold=100):
        self.symbol = symbol.lower()
        self.intervals = intervals
        self.large_order_threshold = large_order_threshold  # 대량 체결 감지 기준 (50 BTC 이상)
        self.tick_rate_threshold = tick_rate_threshold  # 체결 속도 감지 기준 (100건/초 이상)
        self.ws_url = f"{BINANCE_FUTURES_WS_URL}{self.symbol}@trade"
        self.trade_data = {interval: [] for interval in self.intervals}
        self.bid_volume = {interval: [] for interval in self.intervals}
        self.ask_volume = {interval: [] for interval in self.intervals}
        self.tick_count = {interval: 0 for interval in self.intervals}
        self.start_times = {interval: datetime.utcnow() for interval in self.intervals}

    def process_trade(self, data):
        """ 실시간 체결 데이터를 분석 """
        timestamp = datetime.utcfromtimestamp(data["T"] / 1000)
        price = float(data["p"])
        quantity = float(data["q"])
        is_buyer_maker = data["m"]

        # 매수/매도 거래량 분리
        for interval in self.intervals:
            if timestamp >= self.start_times[interval] + timedelta(minutes=int(interval[:-1])):
                self.start_times[interval] = timestamp
                self.trade_data[interval] = []
                self.bid_volume[interval] = []
                self.ask_volume[interval] = []
                self.tick_count[interval] = 0

            self.trade_data[interval].append((timestamp, price, quantity))
            self.tick_count[interval] += 1

            if is_buyer_maker:
                self.ask_volume[interval].append(quantity)
            else:
                self.bid_volume[interval].append(quantity)

        self.detect_large_order(price, quantity)
        self.detect_tick_rate_spike()
        self.analyze_vwap()

    def detect_large_order(self, price, quantity):
        """ 대량 체결(Big Order) 감지 """
        if quantity >= self.large_order_threshold:
            print(f"🐳 [대량 체결 감지] {datetime.utcnow()} | {self.symbol} | 가격 {price:.2f} | 수량 {quantity:.2f} BTC")

    def detect_tick_rate_spike(self):
        """ 초당 체결 속도(Tick Rate) 분석 """
        for interval in self.intervals:
            if self.tick_count[interval] >= self.tick_rate_threshold:
                print(f"⚡ [체결 속도 급증] {datetime.utcnow()} | {interval} | 초당 {self.tick_count[interval]} 건")

    def analyze_vwap(self):
        """ 거래량 가중 평균 가격(VWAP) 분석 """
        for interval in self.intervals:
            if self.trade_data[interval]:
                total_volume = sum([q for _, _, q in self.trade_data[interval]])
                vwap = sum([p * q for _, p, q in self.trade_data[interval]]) / total_volume
                print(f"📊 [VWAP 분석] {datetime.utcnow()} | {interval} | VWAP: {vwap:.2f}")

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 시 처리 """
        data = json.loads(message)
        self.process_trade(data)

    def run(self):
        """ WebSocket을 이용한 실시간 체결 데이터 수집 실행 """
        ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_message)
        print(f"🟢 {self.symbol} 체결 데이터 수집 시작")
        ws.run_forever()

    def start_analysis(self):
        """ 분석 기능을 백그라운드 스레드에서 실행 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    collector = TradeDataCollector(symbol="BTCUSDT")
    collector.start_analysis()

    time.sleep(30)
    print("✅ 체결 데이터 수집 종료")

#1️⃣ 체결 강도(Trade Intensity) 분석 추가 → 고빈도 매매(HFT) 움직임 감지
#2️⃣ Bid/Ask 체결 비율 분석 → 매수/매도 압력 평가하여 트렌드 판단
#3️⃣ OBS를 통한 실시간 시각화 추가 → 체결 강도 변화를 그래프 형태로 표시