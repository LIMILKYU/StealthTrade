import websocket
import json
import os
import logging
import threading
import requests
import mysql.connector
import psycopg2
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

# ✅ 환경 변수 로드
load_dotenv()
BINANCE_WS_BASE = os.getenv("BINANCE_WS_BASE", "wss://fstream.binance.com/ws/")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "trading_data")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "websocket_data")
SELECTED_COINS = os.getenv("SELECTED_COINS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")
USE_MYSQL = os.getenv("USE_MYSQL") == "True"
USE_POSTGRES = os.getenv("USE_POSTGRES") == "True"
USE_MONGO = os.getenv("USE_MONGO") == "True"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class WebSocketListener:
    def __init__(self, depth="100", reconnect_delay=5, ping_interval=30):
        """ ✅ 다중 코인 WebSocket 리스너 """
        self.symbols = [coin.strip().lower() for coin in SELECTED_COINS]
        self.depth = depth
        self.reconnect_delay = reconnect_delay
        self.ws_urls = {symbol: f"{BINANCE_WS_BASE}{symbol}@depth{depth}@100ms" for symbol in self.symbols}
        
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

    def process_data(self, data, symbol):
        """ ✅ WebSocket 데이터 처리 및 저장 """
        timestamp = datetime.utcnow()
        row = {"timestamp": timestamp, "symbol": symbol.upper(), "data": data}

        # ✅ MongoDB 저장
        if USE_MONGO:
            self.collection.insert_one(row)

        # ✅ MySQL 저장
        if USE_MYSQL:
            sql = "INSERT INTO websocket_data (timestamp, symbol, data) VALUES (%s, %s, %s)"
            self.mysql_cursor.execute(sql, (timestamp, symbol.upper(), json.dumps(data)))
            self.mysql_conn.commit()

        # ✅ PostgreSQL 저장
        if USE_POSTGRES:
            sql = "INSERT INTO websocket_data (timestamp, symbol, data) VALUES (%s, %s, %s)"
            self.postgres_cursor.execute(sql, (timestamp, symbol.upper(), json.dumps(data)))
            self.postgres_conn.commit()

        logging.info(f"✅ [WebSocket 데이터 저장] {symbol.upper()} - {timestamp}")

    def on_message(self, ws, message, symbol):
        """ ✅ WebSocket 메시지 처리 """
        data = json.loads(message)
        self.process_data(data, symbol)

    def on_error(self, ws, error):
        logging.error(f"🚨 WebSocket 오류 발생: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logging.warning("⚠️ WebSocket 연결 종료! 5초 후 재연결...")
        time.sleep(self.reconnect_delay)
        self.start_websocket()

    def send_telegram_alert(self, message):
        """ ✅ Telegram 알림 전송 """
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.post(url, data=payload)

    def start_websocket(self):
        """ ✅ 다중 WebSocket 실행 (각 코인별 호가 데이터 수집) """
        for symbol, ws_url in self.ws_urls.items():
            ws = websocket.WebSocketApp(ws_url,
                                        on_message=lambda ws, msg: self.on_message(ws, msg, symbol),
                                        on_error=self.on_error,
                                        on_close=self.on_close)
            threading.Thread(target=ws.run_forever).start()

# ✅ 사용 예시
if __name__ == "__main__":
    listener = WebSocketListener()
    listener.start_websocket()
