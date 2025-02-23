import websocket
import json
import os
import logging
import pandas as pd
import mysql.connector
import psycopg2
import time
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict
import requests

# ✅ 환경 변수 로드
load_dotenv()
BINANCE_WS_URL = os.getenv("BINANCE_FUTURES_WS_URL", "wss://fstream.binance.com/ws/")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "trading_data")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "spoofing_orders")
SELECTED_COINS = os.getenv("SELECTED_COINS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")
USE_MYSQL = os.getenv("USE_MYSQL") == "True"
USE_POSTGRES = os.getenv("USE_POSTGRES") == "True"
USE_MONGO = os.getenv("USE_MONGO") == "True"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class SpoofingDetector:
    def __init__(self, depth=20, threshold_ratio=0.02, cancel_time_threshold=0.5):
        """ ✅ 다중 코인 스푸핑 주문 탐지 클래스 """
        self.symbols = [coin.strip().lower() for coin in SELECTED_COINS]
        self.depth = depth
        self.threshold_ratio = threshold_ratio  # 주문 비율 기준 (예: 2% 이상 비정상 주문)
        self.cancel_time_threshold = cancel_time_threshold  # 주문 취소까지 걸리는 최대 허용 시간 (초)
        self.ws_urls = {symbol: f"{BINANCE_WS_URL}{symbol}@depth{depth}@100ms" for symbol in self.symbols}
        self.recent_orders = {symbol: defaultdict(dict) for symbol in self.symbols}  # 주문 ID별 생성 & 취소 시간 기록

        # ✅ 데이터베이스 설정
        if USE_MONGO:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client[MONGO_DB]
            self.collection = self.db[MONGO_COLLECTION]

        if USE_MYSQL:
            self.mysql_conn = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE")
            )
            self.mysql_cursor = self.mysql_conn.cursor()

        if USE_POSTGRES:
            self.postgres_conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                database=os.getenv("POSTGRES_DATABASE")
            )
            self.postgres_cursor = self.postgres_conn.cursor()

    def detect_spoofing(self, data, symbol):
        """ ✅ 스푸핑 주문 탐지 """
        timestamp = datetime.utcnow()
        bids = {float(bid[0]): float(bid[1]) for bid in data["bids"]}
        asks = {float(ask[0]): float(ask[1]) for ask in data["asks"]}

        # ✅ 기존 주문과 비교하여 비정상적인 주문 취소 여부 감지
        for price, size in list(self.recent_orders[symbol].items()):
            if price not in bids and price not in asks:
                cancel_time = (timestamp - size["timestamp"]).total_seconds()
                if cancel_time < self.cancel_time_threshold:
                    spoofing_order = {
                        "timestamp": timestamp,
                        "symbol": symbol.upper(),
                        "price": price,
                        "size": size["size"],
                        "cancel_time": cancel_time
                    }

                    # ✅ Telegram 알림 전송
                    self.send_telegram_alert(f"🚨 [스푸핑 감지] {symbol} {price} {size['size']}개 주문 취소됨 (취소 속도: {cancel_time:.2f}s)")

                    # ✅ MongoDB 저장
                    if USE_MONGO:
                        self.collection.insert_one(spoofing_order)

                    # ✅ MySQL 저장
                    if USE_MYSQL:
                        sql = "INSERT INTO spoofing_orders (timestamp, symbol, price, size, cancel_time) VALUES (%s, %s, %s, %s, %s)"
                        self.mysql_cursor.execute(sql, (
                            spoofing_order["timestamp"], spoofing_order["symbol"],
                            spoofing_order["price"], spoofing_order["size"], spoofing_order["cancel_time"]
                        ))
                        self.mysql_conn.commit()

                    # ✅ PostgreSQL 저장
                    if USE_POSTGRES:
                        sql = "INSERT INTO spoofing_orders (timestamp, symbol, price, size, cancel_time) VALUES (%s, %s, %s, %s, %s)"
                        self.postgres_cursor.execute(sql, (
                            spoofing_order["timestamp"], spoofing_order["symbol"],
                            spoofing_order["price"], spoofing_order["size"], spoofing_order["cancel_time"]
                        ))
                        self.postgres_conn.commit()

                    logging.info(f"✅ [스푸핑 감지] {spoofing_order}")

                del self.recent_orders[symbol][price]

        # ✅ 새로운 주문 저장
        for price, size in bids.items():
            self.recent_orders[symbol][price] = {"timestamp": timestamp, "size": size}
        for price, size in asks.items():
            self.recent_orders[symbol][price] = {"timestamp": timestamp, "size": size}

    def send_telegram_alert(self, message):
        """ ✅ Telegram 알림 전송 """
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.post(url, data=payload)

    def on_message(self, ws, message, symbol):
        """ ✅ WebSocket 메시지 처리 """
        data = json.loads(message)
        self.detect_spoofing(data, symbol)

    def on_error(self, ws, error):
        logging.error(f"🚨 WebSocket 오류 발생: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logging.warning("⚠️ WebSocket 연결 종료! 5초 후 재연결...")
        time.sleep(5)
        self.start_websocket()

    def start_websocket(self):
        """ ✅ 다중 WebSocket 실행 (각 코인별 스푸핑 탐지) """
        for symbol, ws_url in self.ws_urls.items():
            ws = websocket.WebSocketApp(ws_url,
                                        on_message=lambda ws, msg: self.on_message(ws, msg, symbol),
                                        on_error=self.on_error,
                                        on_close=self.on_close)
            ws.run_forever()

# ✅ 사용 예시
if __name__ == "__main__":
    detector = SpoofingDetector()
    detector.start_websocket()
