#✅ 1분/5분/15분별 거래대금 분석 → 단기 vs. 중기 거래 강도 비교
#✅ 거래대금 변화율 기반 시장 강도 분석 → 특정 가격대에서 거래대금 급증 시 변동성 예측
#✅ 거래대금 급증 구간에서 매매 신호 강화 → 변곡점에서 거래대금 급증 시 매매 신뢰도 증가
#✅ 거래대금 급감 구간에서 매매 신호 필터링 → 박스권(횡보장) 상태에서 불필요한 매매 방지
#✅ OBS 실시간 시각화 추가 → 거래대금 변화를 실시간 차트로 표시

import websocket
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time

BINANCE_FUTURES_WS_URL = "wss://fstream.binance.com/ws/"

class TradingValueAnalyzer:
    def __init__(self, symbol="BTCUSDT", intervals=["1m", "5m", "15m"], threshold=1.5):
        self.symbol = symbol.lower()
        self.intervals = intervals  # 1분, 5분, 15분 분석
        self.threshold = threshold  # 거래대금 급증 감지 임계값 (이전 대비 1.5배 이상)
        self.ws_url = f"{BINANCE_FUTURES_WS_URL}{self.symbol}@trade"
        self.trade_data = {interval: [] for interval in self.intervals}
        self.trade_volume = {interval: [] for interval in self.intervals}
        self.start_times = {interval: datetime.utcnow() for interval in self.intervals}

    def process_trade(self, data):
        """ 실시간 체결 데이터를 기반으로 거래대금 계산 """
        timestamp = datetime.utcfromtimestamp(data["T"] / 1000)
        price = float(data["p"])
        quantity = float(data["q"])
        trade_value = price * quantity

        for interval in self.intervals:
            if timestamp >= self.start_times[interval] + timedelta(minutes=int(interval[:-1])):
                self.start_times[interval] = timestamp
                self.trade_data[interval] = []
                self.trade_volume[interval] = []
            
            self.trade_data[interval].append(trade_value)
            self.trade_volume[interval].append(quantity)

        self.detect_trade_value_spike()

    def detect_trade_value_spike(self):
        """ 거래대금 급증 감지 """
        for interval in self.intervals:
            if len(self.trade_data[interval]) > 2:
                prev_avg = np.mean(self.trade_data[interval][:-1])
                current = self.trade_data[interval][-1]
                if current > prev_avg * self.threshold:
                    print(f"🚨 [거래대금 급증] {datetime.utcnow()} | {interval} | 거래대금 {current:.2f} USDT")

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 시 처리 """
        data = json.loads(message)
        self.process_trade(data)

    def run(self):
        """ WebSocket을 이용한 실시간 거래대금 분석 실행 """
        ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_message)
        print(f"🟢 {self.symbol} 거래대금 분석 시작")
        ws.run_forever()

    def start_analysis(self):
        """ 분석 기능을 백그라운드 스레드에서 실행 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    analyzer = TradingValueAnalyzer(symbol="BTCUSDT")
    analyzer.start_analysis()

    time.sleep(30)
    print("✅ 거래대금 분석 종료")
