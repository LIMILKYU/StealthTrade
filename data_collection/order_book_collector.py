import requests
import json
import pandas as pd
import websocket
import threading
import time
import mysql.connector
import psycopg2
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from coin_selector import SELECTED_COIN  # 📌 `coin_selector.py`에서 선택된 코인 가져오기

# 환경 변수 로드 (.env에서 API 및 DB 설정 불러오기)
load_dotenv()

BINANCE_FUTURES_WS_URL = os.getenv("BINANCE_FUTURES_WS_URL", "wss://fstream.binance.com/ws/")

class OrderBookCollector:
    def __init__(self, depth=20, save_db=True):
        self.symbol = SELECTED_COIN.lower()  # ✅ `coin_selector.py`에서 선택된 코인 적용
        self.depth = depth
        self.save_db = save_db
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

        # ✅ DB 설정 (MySQL, PostgreSQL, MongoDB 지원)
        self.use_mysql = os.getenv("USE_MYSQL") == "True"
        self.use_postgres = os.getenv("USE_POSTGRES") == "True"
        self.use_mongo = os.getenv("USE_MONGO") == "True"

        if self.use_mysql:
            self.mysql_conn = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE")
            )
            self.mysql_cursor = self.mysql_conn.cursor()

        if self.use_postgres:
            self.postgres_conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                database=os.getenv("POSTGRES_DATABASE")
            )
            self.postgres_cursor = self.postgres_conn.cursor()

        if self.use_mongo:
            self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
            self.mongo_db = self.mongo_client[os.getenv("MONGO_DATABASE")]
            self.mongo_collection = self.mongo_db["order_book"]

    def process_order_book(self, data):
        """ 실시간 호가창 데이터를 처리하여 저장 및 분석 """
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
        self.detect_spoofing(order_data)  # ✅ 스푸핑 감지 추가

        print(f"📊 [{timestamp}] {self.symbol.upper()} | Bid: {best_bid}, Ask: {best_ask}, Spread: {spread}")

        if self.save_db:
            self.save_to_db(order_data)

    def aggregate_data(self, order_data):
        """ 호가창 데이터를 다양한 시간봉으로 변환하여 저장 """
        now = datetime.utcnow()
        for interval, data in self.aggregated_data.items():
            if len(data) == 0 or (now - data[-1]["timestamp"]).seconds >= self.get_interval_seconds(interval):
                data.append(order_data)

    def detect_spoofing(self, order_data):
        """ 스푸핑(고빈도 주문 취소) 감지 """
        top_bid_size = list(order_data["bids"].values())[0] if order_data["bids"] else 0
        top_ask_size = list(order_data["asks"].values())[0] if order_data["asks"] else 0

        if top_bid_size > 1000 or top_ask_size > 1000:
            print(f"🚨 스푸핑 감지! Bid Size: {top_bid_size}, Ask Size: {top_ask_size}")

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

    def save_to_db(self, order_data):
        """ 실시간 호가창 데이터를 MySQL, PostgreSQL, MongoDB에 저장 """
        if not self.save_db:
            return

        record = (order_data["timestamp"], order_data["best_bid"], order_data["best_ask"], order_data["spread"])

        if self.use_mysql:
            query = "INSERT INTO order_book (timestamp, best_bid, best_ask, spread) VALUES (%s, %s, %s, %s)"
            self.mysql_cursor.execute(query, record)
            self.mysql_conn.commit()

        if self.use_postgres:
            query = "INSERT INTO order_book (timestamp, best_bid, best_ask, spread) VALUES (%s, %s, %s, %s)"
            self.postgres_cursor.execute(query, record)
            self.postgres_conn.commit()

        if self.use_mongo:
            self.mongo_collection.insert_one(order_data)

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 시 처리 """
        data = json.loads(message)
        self.process_order_book(data)

    def run(self):
        """ WebSocket을 이용한 실시간 호가창 데이터 수집 실행 """
        while True:
            try:
                ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_message)
                print(f"🟢 {self.symbol.upper()} 호가창 데이터 수집 시작 (depth={self.depth})")
                ws.run_forever()
            except Exception as e:
                print(f"⚠️ WebSocket 재연결 시도 중... ({e})")
                time.sleep(5)  # 5초 후 재연결

    def start_collection(self):
        """ 데이터 수집을 백그라운드 스레드에서 실행 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    collector = OrderBookCollector(depth=20, save_db=True)
    collector.start_collection()

    # 실행 중 10초 후 데이터 저장
    time.sleep(10)
    collector.save_to_csv()
