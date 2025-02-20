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

class TradeDataCollector:
    def __init__(self, intervals=["1m", "5m", "15m"], large_order_threshold=50, tick_rate_threshold=100, save_db=True):
        self.symbol = SELECTED_COIN.lower()  # ✅ `coin_selector.py`에서 선택된 코인 적용
        self.intervals = intervals
        self.large_order_threshold = large_order_threshold  # 대량 체결 감지 기준 (50 BTC 이상)
        self.tick_rate_threshold = tick_rate_threshold  # 체결 속도 감지 기준 (100건/초 이상)
        self.ws_url = f"{BINANCE_FUTURES_WS_URL}{self.symbol}@trade"
        self.trade_data = {interval: deque(maxlen=10) for interval in self.intervals}  # 최근 10개 데이터 저장
        self.bid_volume = {interval: deque(maxlen=10) for interval in self.intervals}
        self.ask_volume = {interval: deque(maxlen=10) for interval in self.intervals}
        self.tick_count = {interval: 0 for interval in self.intervals}
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
            self.mongo_collection = self.mongo_db["trade_data"]

        # ✅ 차트 설정 (OBS 실시간 시각화 지원)
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 5))

    def process_trade(self, data):
        """ 실시간 체결 데이터를 분석 """
        timestamp = datetime.utcfromtimestamp(data["T"] / 1000)
        price = float(data["p"])
        quantity = float(data["q"])
        is_buyer_maker = data["m"]

        # 매수/매도 거래량 분리
        for interval in self.intervals:
            if timestamp >= self.start_times[interval] + timedelta(minutes=int(interval[:-1])):
                self.start_times[interval] = timestamp
                self.trade_data[interval].clear()
                self.bid_volume[interval].clear()
                self.ask_volume[interval].clear()
                self.tick_count[interval] = 0

            self.trade_data[interval].append((timestamp, price, quantity))
            self.tick_count[interval] += 1

            if is_buyer_maker:
                self.ask_volume[interval].append(quantity)
            else:
                self.bid_volume[interval].append(quantity)

        self.detect_large_order(price, quantity)
        self.detect_tick_rate_spike()
        self.analyze_vwap()
        self.update_chart()

    def detect_large_order(self, price, quantity):
        """ 대량 체결(Big Order) 감지 """
        if quantity >= self.large_order_threshold:
            log_entry = {
                "timestamp": datetime.utcnow(),
                "price": price,
                "quantity": quantity
            }
            print(f"🐳 [대량 체결 감지] {log_entry}")
            self.send_telegram_alert(log_entry)
            if self.save_db:
                self.save_to_db(log_entry)

    def detect_tick_rate_spike(self):
        """ 초당 체결 속도(Tick Rate) 분석 """
        for interval in self.intervals:
            if self.tick_count[interval] >= self.tick_rate_threshold:
                print(f"⚡ [체결 속도 급증] {datetime.utcnow()} | {interval} | 초당 {self.tick_count[interval]} 건")

    def analyze_vwap(self):
        """ 거래량 가중 평균 가격(VWAP) 분석 """
        for interval in self.intervals:
            if self.trade_data[interval]:
                total_volume = sum([q for _, _, q in self.trade_data[interval]])
                vwap = sum([p * q for _, p, q in self.trade_data[interval]]) / total_volume
                print(f"📊 [VWAP 분석] {datetime.utcnow()} | {interval} | VWAP: {vwap:.2f}")

    def send_telegram_alert(self, log_entry):
        """ 대량 체결 감지 시 Telegram 알림 전송 """
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            message = (f"🚨 [대량 체결 감지] {self.symbol.upper()}\n"
                       f"🕒 시간: {log_entry['timestamp']}\n"
                       f"💰 가격: {log_entry['price']:.2f}\n"
                       f"📈 체결량: {log_entry['quantity']:.2f} BTC")
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.post(url, data=payload)

    def save_to_db(self, log_entry):
        """ 대량 체결 데이터를 MySQL, PostgreSQL, MongoDB에 저장 """
        if not self.save_db:
            return

        record = (log_entry["timestamp"], log_entry["price"], log_entry["quantity"])

        if self.use_mysql:
            query = "INSERT INTO trade_data (timestamp, price, quantity) VALUES (%s, %s, %s)"
            self.mysql_cursor.execute(query, record)
            self.mysql_conn.commit()

        if self.use_postgres:
            query = "INSERT INTO trade_data (timestamp, price, quantity) VALUES (%s, %s, %s)"
            self.postgres_cursor.execute(query, record)
            self.postgres_conn.commit()

        if self.use_mongo:
            self.mongo_collection.insert_one(log_entry)

    def update_chart(self):
        """ 체결 강도를 실시간 시각화 (OBS 연동) """
        self.ax.clear()
        for interval in self.intervals:
            if len(self.trade_data[interval]) > 1:
                times = [i for i in range(len(self.trade_data[interval]))]
                self.ax.plot(times, [q for _, _, q in self.trade_data[interval]], label=f"{interval} 체결 강도", marker="o")

        self.ax.set_title(f"Trade Intensity ({self.symbol.upper()})")
        self.ax.legend()
        plt.draw()
        plt.pause(0.01)

if __name__ == "__main__":
    collector = TradeDataCollector(save_db=True)
    collector.start_analysis()

    time.sleep(30)
    print("✅ 체결 데이터 수집 종료")
