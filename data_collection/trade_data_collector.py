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
from datetime import datetime, timedelta
from collections import deque
import requests

# ✅ 환경 변수 로드
load_dotenv()
BINANCE_WS_URL = os.getenv("BINANCE_FUTURES_WS_URL", "wss://fstream.binance.com/ws/")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "trading_data")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "trade_data")
SELECTED_COINS = os.getenv("SELECTED_COINS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")
USE_MYSQL = os.getenv("USE_MYSQL") == "True"
USE_POSTGRES = os.getenv("USE_POSTGRES") == "True"
USE_MONGO = os.getenv("USE_MONGO") == "True"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class TradeDataCollector:
    def __init__(self, large_order_threshold=50, tick_rate_threshold=100):
        """ ✅ 다중 코인 실시간 체결 데이터 수집 클래스 """
        self.symbols = [coin.strip().lower() for coin in SELECTED_COINS]
        self.ws_urls = {symbol: f"{BINANCE_WS_URL}{symbol}@trade" for symbol in self.symbols}
        self.large_order_threshold = large_order_threshold  # 대량 체결 감지 기준 (50 BTC 이상)
        self.tick_rate_threshold = tick_rate_threshold  # 체결 속도 감지 기준 (100건/초 이상)
        self.trade_data = {symbol: deque(maxlen=100) for symbol in self.symbols}
        self.tick_count = {symbol: 0 for symbol in self.symbols}
        self.start_times = {symbol: datetime.utcnow() for symbol in self.symbols}

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

    def process_trade(self, data, symbol):
        """ ✅ 실시간 체결 데이터 처리 및 저장 """
        timestamp = datetime.utcfromtimestamp(data["T"] / 1000)
        price = float(data["p"])
        quantity = float(data["q"])
        is_buyer_maker = data["m"]

        trade = {
            "timestamp": timestamp,
            "symbol": symbol.upper(),
            "price": price,
            "quantity": quantity,
            "is_buyer_maker": is_buyer_maker
        }

        self.trade_data[symbol].append(trade)

        # ✅ 대량 체결 감지
        if quantity >= self.large_order_threshold:
            self.send_telegram_alert(f"🚨 [대량 체결] {symbol} {quantity}개 체결 (가격: {price})")

        # ✅ 체결 속도 감지
        self.tick_count[symbol] += 1
        if (datetime.utcnow() - self.start_times[symbol]).total_seconds() >= 1:
            if self.tick_count[symbol] > self.tick_rate_threshold:
                self.send_telegram_alert(f"⚡ [체결 속도 급증] {symbol} {self.tick_count[symbol]}건/초")
            self.tick_count[symbol] = 0
            self.start_times[symbol] = datetime.utcnow()

        # ✅ 데이터 저장 (MongoDB, MySQL, PostgreSQL)
        self.store_data(trade)

    def store_data(self, trade):
        """ ✅ 데이터 저장 (MongoDB, MySQL, PostgreSQL) """
        if USE_MONGO:
            self.collection.insert_one(trade)

        if USE_MYSQL:
            sql = "INSERT INTO trade_data (timestamp, symbol, price, quantity, is_buyer_maker) VALUES (%s, %s, %s, %s, %s)"
            self.mysql_cursor.execute(sql, (
                trade["timestamp"], trade["symbol"], trade["price"],
                trade["quantity"], trade["is_buyer_maker"]
            ))
            self.mysql_conn.commit()

        if USE_POSTGRES:
            sql = "INSERT INTO trade_data (timestamp, symbol, price, quantity, is_buyer_maker) VALUES (%s, %s, %s, %s, %s)"
            self.postgres_cursor.execute(sql, (
                trade["timestamp"], trade["symbol"], trade["price"],
                trade["quantity"], trade["is_buyer_maker"]
            ))
            self.postgres_conn.commit()

    def send_telegram_alert(self, message):
        """ ✅ Telegram 알림 전송 """
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.post(url, data=payload)

    def on_message(self, ws, message, symbol):
        """ ✅ WebSocket 메시지 처리 """
        data = json.loads(message)
        self.process_trade(data, symbol)

    def on_error(self, ws, error):
        logging.error(f"🚨 WebSocket 오류 발생: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logging.warning("⚠️ WebSocket 연결 종료! 5초 후 재연결...")
        time.sleep(5)
        self.start_websocket()

    def start_websocket(self):
        """ ✅ 다중 WebSocket 실행 (각 코인별 실시간 체결 데이터 수집) """
        for symbol, ws_url in self.ws_urls.items():
            ws = websocket.WebSocketApp(ws_url,
                                        on_message=lambda ws, msg: self.on_message(ws, msg, symbol),
                                        on_error=self.on_error,
                                        on_close=self.on_close)
            ws.run_forever()

# ✅ 사용 예시
if __name__ == "__main__":
    collector = TradeDataCollector()
    collector.start_websocket()
