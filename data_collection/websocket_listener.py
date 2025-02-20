import websocket
import json
import time
import os
import threading
import logging
import requests
import mysql.connector
import psycopg2
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from select_coin import SELECTED_COIN  # ✅ 선택된 코인 가져오기

# 환경 변수 로드
load_dotenv()

# ✅ Binance WebSocket URL
BINANCE_WS_BASE = os.getenv("BINANCE_WS_BASE", "wss://fstream.binance.com/ws/")

# ✅ Telegram 알림 설정
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ Slack 알림 설정
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# ✅ DB 설정
USE_MYSQL = os.getenv("USE_MYSQL") == "True"
USE_POSTGRES = os.getenv("USE_POSTGRES") == "True"
USE_MONGO = os.getenv("USE_MONGO") == "True"

# ✅ MySQL 연결
if USE_MYSQL:
    mysql_conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )
    mysql_cursor = mysql_conn.cursor()

# ✅ PostgreSQL 연결
if USE_POSTGRES:
    postgres_conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DATABASE")
    )
    postgres_cursor = postgres_conn.cursor()

# ✅ MongoDB 연결
if USE_MONGO:
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    mongo_db = mongo_client[os.getenv("MONGO_DATABASE")]
    mongo_collection = mongo_db["order_book"]

# ✅ 로깅 설정
logging.basicConfig(
    filename="websocket_listener.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class WebSocketListener:
    def __init__(self, depth="100", reconnect_delay=5, ping_interval=30, save_to_file=True):
        """
        :param depth: 호가창 깊이 (5, 10, 20, 50, 100 등)
        :param reconnect_delay: 재연결 대기 시간 (초)
        :param ping_interval: Ping 신호를 보낼 간격 (초)
        :param save_to_file: JSON 파일로 데이터 저장 여부
        """
        self.symbol = SELECTED_COIN.lower()  # ✅ `select_coin.py`에서 심볼 가져오기
        self.depth = depth
        self.reconnect_delay = reconnect_delay
        self.ping_interval = ping_interval
        self.save_to_file = save_to_file
        self.ws = None
        self.ws_url = f"{BINANCE_WS_BASE}{self.symbol}@depth{self.depth}@100ms"

    def send_telegram_alert(self, message):
        """ WebSocket 오류 또는 종료 시 Telegram 알림 전송 """
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.post(url, data=payload)
        else:
            logging.warning("⚠️ Telegram 설정이 누락되었습니다. .env 파일을 확인하세요.")

    def send_slack_alert(self, message):
        """ WebSocket 오류 또는 종료 시 Slack 알림 전송 """
        if SLACK_WEBHOOK_URL:
            requests.post(SLACK_WEBHOOK_URL, json={"text": message})
        else:
            logging.warning("⚠️ Slack 설정이 누락되었습니다. .env 파일을 확인하세요.")

    def save_to_db(self, data):
        """ 실시간 데이터를 MySQL, PostgreSQL, MongoDB에 저장 """
        timestamp = datetime.utcnow()

        if USE_MYSQL:
            query = "INSERT INTO order_book (timestamp, symbol, bid, ask, spread) VALUES (%s, %s, %s, %s, %s)"
            mysql_cursor.execute(query, (timestamp, self.symbol.upper(), data["bids"][0][0], data["asks"][0][0], data["spread"]))
            mysql_conn.commit()

        if USE_POSTGRES:
            query = "INSERT INTO order_book (timestamp, symbol, bid, ask, spread) VALUES (%s, %s, %s, %s, %s)"
            postgres_cursor.execute(query, (timestamp, self.symbol.upper(), data["bids"][0][0], data["asks"][0][0], data["spread"]))
            postgres_conn.commit()

        if USE_MONGO:
            mongo_collection.insert_one({
                "timestamp": timestamp,
                "symbol": self.symbol.upper(),
                "bid": data["bids"][0][0],
                "ask": data["asks"][0][0],
                "spread": data["spread"]
            })

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 후 처리 """
        data = json.loads(message)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # 스프레드 계산
        best_bid = float(data["bids"][0][0])
        best_ask = float(data["asks"][0][0])
        spread = best_ask - best_bid
        data["spread"] = spread

        # Bid-Ask Imbalance 감지
        total_bids = sum(float(bid[1]) for bid in data["bids"])
        total_asks = sum(float(ask[1]) for ask in data["asks"])
        imbalance = abs(total_bids - total_asks) / (total_bids + total_asks)

        # 비정상적인 호가(스푸핑) 감지
        if imbalance > 0.7:
            logging.warning(f"🚨 [Bid-Ask Imbalance] {timestamp} | {self.symbol.upper()} | 불균형: {imbalance:.2f}")
            self.send_telegram_alert(f"🚨 Bid-Ask Imbalance 발생!\n🔹 {self.symbol.upper()} 불균형: {imbalance:.2f}")

        logging.info(f"📊 [{timestamp}] {self.symbol.upper()} | Bid: {best_bid}, Ask: {best_ask}, Spread: {spread}")

        # 데이터 저장
        self.save_to_db(data)

        # JSON 파일 저장
        if self.save_to_file:
            with open("order_book_data.json", "a") as f:
                json.dump({"timestamp": timestamp, "data": data}, f)
                f.write("\n")

    def run(self):
        """ WebSocket 실행 """
        while True:
            try:
                ws = websocket.WebSocketApp(
                    self.ws_url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                ws.on_open = self.on_open
                ws.run_forever(ping_interval=self.ping_interval, ping_timeout=10)
            except Exception as e:
                logging.error(f"⚠️ WebSocket 재연결 실패: {e}")
                time.sleep(self.reconnect_delay)

if __name__ == "__main__":
    listener = WebSocketListener(depth="20")
    listener.run()
