import websocket
import json
import os
import logging
import pandas as pd
import time
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# ✅ 환경 변수 로드
load_dotenv()
BINANCE_WS_URL = os.getenv("BINANCE_FUTURES_WS_URL", "wss://fstream.binance.com/ws/")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "trading_data")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "order_book")
SELECTED_COINS = os.getenv("SELECTED_COINS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")

class OrderBookCollector:
    def __init__(self):
        """ ✅ 다중 코인 & 다중 호가 깊이 분석 (depth5, depth20, depth50, depth100) """
        self.symbols = [coin.strip().lower() for coin in SELECTED_COINS]
        self.depth_levels = [5, 20, 50, 100]
        self.ws_urls = {
            (symbol, depth): f"{BINANCE_WS_URL}{symbol}@depth{depth}@100ms"
            for symbol in self.symbols
            for depth in self.depth_levels
        }
        self.data = {
            (symbol, depth): pd.DataFrame(columns=["timestamp", "bids", "asks"])
            for symbol in self.symbols
            for depth in self.depth_levels
        }
        self.mongo_client = MongoClient(MONGO_URL)
        self.db = self.mongo_client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION]

    def process_order_book(self, data, symbol, depth):
        """ ✅ 호가창 데이터 처리 및 저장 """
        timestamp = datetime.utcnow()
        bids = [(float(bid[0]), float(bid[1])) for bid in data["bids"]]
        asks = [(float(ask[0]), float(ask[1])) for ask in data["asks"]]

        row = {"timestamp": timestamp, "symbol": symbol.upper(), "depth": depth, "bids": bids, "asks": asks}
        self.data[(symbol, depth)] = self.data[(symbol, depth)].append(row, ignore_index=True)

        # ✅ MongoDB 저장
        self.collection.insert_one(row)
        logging.info(f"✅ [호가창 저장] {timestamp} {symbol.upper()} depth{depth} - Bids: {bids[:3]}... Asks: {asks[:3]}...")

    def on_message(self, ws, message, symbol, depth):
        """ ✅ WebSocket 메시지 처리 """
        data = json.loads(message)
        self.process_order_book(data, symbol, depth)

    def on_error(self, ws, error):
        logging.error(f"🚨 WebSocket 오류 발생: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logging.warning("⚠️ WebSocket 연결 종료! 5초 후 재연결...")
        time.sleep(5)
        self.start_websocket()

    def start_websocket(self):
        """ ✅ 다중 WebSocket 실행 (각 코인별 depth5, depth20, depth50, depth100) """
        for (symbol, depth), ws_url in self.ws_urls.items():
            ws = websocket.WebSocketApp(ws_url,
                                        on_message=lambda ws, msg: self.on_message(ws, msg, symbol, depth),
                                        on_error=self.on_error,
                                        on_close=self.on_close)
            ws.run_forever()

# ✅ 사용 예시
if __name__ == "__main__":
    collector = OrderBookCollector()
    collector.start_websocket()
