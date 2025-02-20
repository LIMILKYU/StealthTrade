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
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
from collections import deque
from dotenv import load_dotenv
from coin_selector import SELECTED_COIN  # 📌 `coin_selector.py`에서 선택된 코인 가져오기

# 환경 변수 로드 (.env에서 API 및 DB 설정 불러오기)
load_dotenv()

BINANCE_FUTURES_WS_URL = os.getenv("BINANCE_FUTURES_WS_URL", "wss://fstream.binance.com/ws/")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class TradingValueAnalyzer:
    def __init__(self, intervals=["1m", "5m", "15m"], threshold=1.5, save_db=True):
        self.symbol = SELECTED_COIN.lower()  # ✅ `coin_selector.py`에서 선택된 코인 적용
        self.intervals = intervals  # 1분, 5분, 15분 분석
        self.threshold = threshold  # 거래대금 급증 감지 임계값 (이전 대비 1.5배 이상)
        self.ws_url = f"{BINANCE_FUTURES_WS_URL}{self.symbol}@trade"
        self.trade_data = {interval: deque(maxlen=10) for interval in self.intervals}  # 최근 10개 데이터 저장
        self.trade_volume = {interval: deque(maxlen=10) for interval in self.intervals}
        self.start_times = {interval: datetime.utcnow() for interval in self.intervals}
        self.save_db = save_db

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
            self.mongo_collection = self.mongo_db["trading_volume"]

        # ✅ 차트 설정 (OBS 실시간 시각화 지원)
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 5))

    def process_trade(self, data):
        """ 실시간 체결 데이터를 기반으로 거래대금 계산 """
        timestamp = datetime.utcfromtimestamp(data["T"] / 1000)
        price = float(data["p"])
        quantity = float(data["q"])
        trade_value = price * quantity

        for interval in self.intervals:
            if timestamp >= self.start_times[interval] + timedelta(minutes=int(interval[:-1])):
                self.start_times[interval] = timestamp
                self.trade_data[interval].clear()
                self.trade_volume[interval].clear()
            
            self.trade_data[interval].append(trade_value)
            self.trade_volume[interval].append(quantity)

        self.detect_trade_value_spike()

    def detect_trade_value_spike(self):
        """ 거래대금 급증 감지 """
        for interval in self.intervals:
            if len(self.trade_data[interval]) > 2:
                prev_avg = np.mean(list(self.trade_data[interval])[:-1])
                current = self.trade_data[interval][-1]
                if current > prev_avg * self.threshold:
                    log_entry = {
                        "timestamp": datetime.utcnow(),
                        "interval": interval,
                        "trade_value": current
                    }
                    print(f"🚨 [거래대금 급증] {log_entry}")
                    self.send_telegram_alert(log_entry)
                    if self.save_db:
                        self.save_to_db(log_entry)
                    self.update_chart()

    def send_telegram_alert(self, log_entry):
        """ 거래대금 급증 감지 시 Telegram 알림 전송 """
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            message = (f"🚨 [거래대금 급증] {self.symbol.upper()}\n"
                       f"🕒 시간: {log_entry['timestamp']}\n"
                       f"📊 구간: {log_entry['interval']}\n"
                       f"💰 거래대금: {log_entry['trade_value']:.2f} USDT")
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.post(url, data=payload)

    def save_to_db(self, log_entry):
        """ 거래대금 분석 데이터를 MySQL, PostgreSQL, MongoDB에 저장 """
        if not self.save_db:
            return

        record = (log_entry["timestamp"], log_entry["interval"], log_entry["trade_value"])

        if self.use_mysql:
            query = "INSERT INTO trading_volume (timestamp, interval, trade_value) VALUES (%s, %s, %s)"
            self.mysql_cursor.execute(query, record)
            self.mysql_conn.commit()

        if self.use_postgres:
            query = "INSERT INTO trading_volume (timestamp, interval, trade_value) VALUES (%s, %s, %s)"
            self.postgres_cursor.execute(query, record)
            self.postgres_conn.commit()

        if self.use_mongo:
            self.mongo_collection.insert_one(log_entry)

    def update_chart(self):
        """ 거래대금 변화를 실시간 시각화 (OBS 연동) """
        self.ax.clear()
        for interval in self.intervals:
            if len(self.trade_data[interval]) > 1:
                times = [i for i in range(len(self.trade_data[interval]))]
                self.ax.plot(times, list(self.trade_data[interval]), label=f"{interval} 거래대금", marker="o")

        self.ax.set_title(f"Trading Volume Analysis ({self.symbol.upper()})")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Trading Volume (USDT)")
        self.ax.legend()
        plt.draw()
        plt.pause(0.01)

    def on_message(self, ws, message):
        """ WebSocket 메시지 수신 시 처리 """
        data = json.loads(message)
        self.process_trade(data)

    def run(self):
        """ WebSocket 실행 (자동 재연결 포함) """
        while True:
            try:
                ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_message)
                print(f"🟢 {self.symbol.upper()} 거래대금 분석 시작")
                ws.run_forever()
            except Exception as e:
                print(f"⚠️ WebSocket 재연결 시도 중... ({e})")
                time.sleep(5)

    def start_analysis(self):
        """ 분석 기능을 백그라운드 스레드에서 실행 """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    analyzer = TradingValueAnalyzer(save_db=True)
    analyzer.start_analysis()

    time.sleep(30)
    print("✅ 거래대금 분석 종료")
