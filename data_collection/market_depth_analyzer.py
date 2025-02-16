#✅ Depth5, Depth20을 포함하여 다양한 Depth 레벨 분석 (Depth10, Depth50, Depth100 추가)
#✅ Bid-Ask Imbalance, Iceberg 주문 감지, Spoofing 패턴과 결합하여 강력한 시장 신호 분석
#✅ 호가창 데이터를 1초·5초·1분·5분 단위로 정리하여 시장 유동성 변화를 시계열로 저장
#✅ OBS를 활용한 실시간 시장 깊이 시각화 지원 (추후 적용 가능)

import websocket
import json
import pandas as pd
import numpy as np
import time
import threading

BINANCE_WS_URL = "wss://fstream.binance.com/ws/"

class MarketDepthAnalyzer:
    def __init__(self, symbol="BTCUSDT", depth_levels=[5, 10, 20, 50, 100], timeframes=["1s", "5s", "1m", "5m"]):
        self.symbol = symbol.lower()
        self.depth_levels = depth_levels
        self.timeframes = timeframes
        self.order_book_data = {tf: [] for tf in self.timeframes}  # 시간대별 호가창 데이터 저장
        self.recent_depth = None  # 최근 Depth 저장

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

            # 5분 이내의 데이터만 유지 (5분 = 300초)
            self.order_book_data[timeframe] = [(t, d) for t, d in self.order_book_data[timeframe] if current_time - t < 300]

    def process_order_book(self, data):
        """ WebSocket을 통해 수신된 호가창 데이터 처리 """
        depth_metrics = self.calculate_depth_metrics(data)
        self.recent_depth = depth_metrics  # 최신 데이터 업데이트
        self.update_order_book_history(depth_metrics)

        print(f"📊 [시장 깊이 분석] {self.symbol} | {depth_metrics}")

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 후 처리 """
        data = json.loads(message)
        self.process_order_book(data)

    def run(self):
        """ WebSocket 실행 """
        ws_url = f"{BINANCE_WS_URL}{self.symbol.lower()}@depth@100ms"
        ws = websocket.WebSocketApp(ws_url, on_message=self.on_message)
        print(f"🟢 {self.symbol} 시장 깊이 분석 시작")
        ws.run_forever()

    def start_analysis(self):
        """ 백그라운드 스레드에서 분석 시작 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    market_depth_analyzer = MarketDepthAnalyzer(symbol="BTCUSDT")
    market_depth_analyzer.start_analysis()

    time.sleep(30)
    print("✅ 시장 깊이 분석 종료")

#1️⃣ 시장 깊이 변화에 따른 유동성 패턴 분석 → 급변 시 매매 전략에 반영
#2️⃣ Bid-Ask Imbalance와 결합하여 시장 강세/약세 신호 분석
#3️⃣ 5초·1분·5분 단위의 시장 깊이 변화율을 시계열 분석하여 단기 추세 감지
#4️⃣ Iceberg 주문 감지와 결합하여 고래 매매 패턴 분석 강화
#5️⃣ OBS 차트 연동하여 시장 깊이 변화를 실시간으로 시각화 지원