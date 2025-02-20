import requests
import json
import pandas as pd
import numpy as np
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
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class SpoofingDetector:
    def __init__(self, depth=20, threshold_ratio=0.02, cancel_time_threshold=0.5, save_db=True):
        self.symbol = SELECTED_COIN.lower()  # ✅ `coin_selector.py`에서 선택된 코인 적용
        self.depth = depth
        self.threshold_ratio = threshold_ratio  # 주문 비율 기준 (예: 2% 이상 비정상 주문)
        self.cancel_time_threshold = cancel_time_threshold  # 주문 취소까지 걸리는 최대 허용 시간 (초)
        self.save_db = save_db
        self.ws_url = f"{BINANCE_FUTURES_WS_URL}{self.symbol}@depth{self.depth}@100ms"
        self.recent_orders = {}  # 주문 ID별 생성 & 취소 시간 기록

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
            self.mongo_collection = self.mongo_db["spoofing_logs"]

    def detect_spoofing(self, data):
        """ 스푸핑 탐지 로직 실행 """
        timestamp = datetime.utcnow()
        bids = {float(x[0]): float(x[1]) for x in data["bids"]}  # 매수 호가
        asks = {float(x[0]): float(x[1]) for x in data["asks"]}  # 매도 호가

        total_bid_volume = sum(bids.values())
        total_ask_volume = sum(asks.values())

        # ✅ 비정상적으로 큰 주문 감지 (이상치 탐지)
        suspicious_bids = {price: vol for price, vol in bids.items() if vol > total_bid_volume * self.threshold_ratio}
        suspicious_asks = {price: vol for price, vol in asks.items() if vol > total_ask_volume * self.threshold_ratio}

        # ✅ Bid-Ask 불균형 기반 탐지
        bid_ask_imbalance = abs(total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume + 1e-9)
        
        # ✅ 빠른 주문 취소 감지 (일정 시간 내 취소된 주문 확인)
        cancelled_orders = [order_id for order_id, t in self.recent_orders.items() if (timestamp - t).total_seconds() <= self.cancel_time_threshold]
        
        # ✅ 탐지된 이상 현상 기록 및 알림 전송
        if suspicious_bids or suspicious_asks or bid_ask_imbalance > 0.7 or cancelled_orders:
            log_entry = {
                "timestamp": timestamp,
                "suspicious_bids": suspicious_bids,
                "suspicious_asks": suspicious_asks,
                "bid_ask_imbalance": bid_ask_imbalance,
                "cancelled_orders": len(cancelled_orders)
            }
            print(f"🚨 [스푸핑 감지] {log_entry}")

            # ✅ DB 저장
            if self.save_db:
                self.save_to_db(log_entry)

            # ✅ Telegram 알림 전송
            self.send_telegram_alert(log_entry)

    def send_telegram_alert(self, log_entry):
        """ 스푸핑 감지 시 Telegram 알림 전송 """
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            message = (f"🚨 [스푸핑 감지] {self.symbol.upper()}\n"
                       f"🕒 시간: {log_entry['timestamp']}\n"
                       f"📈 Bid-Ask 불균형: {log_entry['bid_ask_imbalance']:.2f}\n"
                       f"⚠️ 이상 매수 주문: {len(log_entry['suspicious_bids'])}\n"
                       f"⚠️ 이상 매도 주문: {len(log_entry['suspicious_asks'])}\n"
                       f"❌ 빠른 취소 주문: {log_entry['cancelled_orders']}")
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.post(url, data=payload)

    def save_to_db(self, log_entry):
        """ 탐지된 스푸핑 데이터를 MySQL, PostgreSQL, MongoDB에 저장 """
        if not self.save_db:
            return

        record = (log_entry["timestamp"], log_entry["bid_ask_imbalance"], len(log_entry["suspicious_bids"]), len(log_entry["suspicious_asks"]), log_entry["cancelled_orders"])

        if self.use_mysql:
            query = "INSERT INTO spoofing_logs (timestamp, bid_ask_imbalance, suspicious_bids, suspicious_asks, cancelled_orders) VALUES (%s, %s, %s, %s, %s)"
            self.mysql_cursor.execute(query, record)
            self.mysql_conn.commit()

        if self.use_postgres:
            query = "INSERT INTO spoofing_logs (timestamp, bid_ask_imbalance, suspicious_bids, suspicious_asks, cancelled_orders) VALUES (%s, %s, %s, %s, %s)"
            self.postgres_cursor.execute(query, record)
            self.postgres_conn.commit()

        if self.use_mongo:
            self.mongo_collection.insert_one(log_entry)

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 시 처리 """
        data = json.loads(message)
        self.detect_spoofing(data)

    def run(self):
        """ WebSocket 실행 (자동 재연결 포함) """
        while True:
            try:
                ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_message)
                print(f"🟢 {self.symbol.upper()} 스푸핑 탐지 시작 (depth={self.depth})")
                ws.run_forever()
            except Exception as e:
                print(f"⚠️ WebSocket 재연결 시도 중... ({e})")
                time.sleep(5)

    def start_detection(self):
        """ 탐지 기능을 백그라운드 스레드에서 실행 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    detector = SpoofingDetector(depth=20, save_db=True)
    detector.start_detection()

    # 10초 후 종료
    time.sleep(10)
    print("✅ 스푸핑 탐지 종료")
