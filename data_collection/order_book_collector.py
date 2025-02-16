#✅ 호가창 데이터 실시간 수집 (WebSocket)
#✅ 다양한 시간봉 변환 지원 (틱 데이터, 1초, 5초, 15초, 1분, 5분, 15분, 1시간)
#✅ 호가 스프레드 분석 추가
#✅ CSV 저장 및 백테스팅 연계 가능

import websocket
import json
import pandas as pd
from datetime import datetime
import threading
import time

# 📌 Binance Futures API
BINANCE_FUTURES_WS_URL = "wss://fstream.binance.com/ws/"

class OrderBookCollector:
    def __init__(self, symbol="BTCUSDT", depth=20):
        self.symbol = symbol.lower()
        self.depth = depth
        self.order_book_data = []
        self.aggregated_data = {
            "1s": [],
            "5s": [],
            "15s": [],
            "1m": [],
            "5m": [],
            "15m": [],
            "1h": []
        }
        self.ws_url = f"{BINANCE_FUTURES_WS_URL}{self.symbol}@depth{self.depth}@100ms"

    def process_order_book(self, data):
        """ 실시간 호가창 데이터를 처리하여 저장 """
        timestamp = datetime.utcnow()
        bids = {float(x[0]): float(x[1]) for x in data["bids"]}  # 매수 호가
        asks = {float(x[0]): float(x[1]) for x in data["asks"]}  # 매도 호가
        best_bid = max(bids.keys()) if bids else None
        best_ask = min(asks.keys()) if asks else None
        spread = best_ask - best_bid if best_bid and best_ask else None

        order_data = {
            "timestamp": timestamp,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "bids": bids,
            "asks": asks
        }
        
        self.order_book_data.append(order_data)
        self.aggregate_data(order_data)

        print(f"📊 [{timestamp}] Bid: {best_bid}, Ask: {best_ask}, Spread: {spread}")

    def aggregate_data(self, order_data):
        """ 호가창 데이터를 다양한 시간봉으로 변환하여 저장 """
        now = datetime.utcnow()
        for interval, data in self.aggregated_data.items():
            if len(data) == 0 or (now - data[-1]["timestamp"]).seconds >= self.get_interval_seconds(interval):
                data.append(order_data)

    def get_interval_seconds(self, interval):
        """ 시간 간격을 초 단위로 변환 """
        interval_mapping = {
            "1s": 1,
            "5s": 5,
            "15s": 15,
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "1h": 3600
        }
        return interval_mapping.get(interval, 60)

    def save_to_csv(self, filename="order_book_data.csv"):
        """ 데이터를 CSV로 저장 """
        if self.order_book_data:
            df = pd.DataFrame(self.order_book_data)
            df.to_csv(filename, index=False)
            print(f"✅ 호가창 데이터 저장 완료: {filename}")

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 시 처리 """
        data = json.loads(message)
        self.process_order_book(data)

    def run(self):
        """ WebSocket을 이용한 실시간 호가창 데이터 수집 실행 """
        ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_message)
        print(f"🟢 {self.symbol} 호가창 데이터 수집 시작 (depth={self.depth})")
        ws.run_forever()

    def start_collection(self):
        """ 데이터 수집을 백그라운드 스레드에서 실행 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()
    
if __name__ == "__main__":
    collector = OrderBookCollector(symbol="BTCUSDT", depth=20)
    collector.start_collection()

    # 실행 중 10초 후 데이터 저장
    time.sleep(10)
    collector.save_to_csv()

#✅ 고빈도(HFT) 및 저빈도(LFT) 분석 조합
#✅ 스푸핑 및 고빈도 트레이더 감지 기능 추가
#✅ SQL 데이터베이스(DB) 저장 기능 추가
#✅ 시장 변동성 분석과 결합 가능