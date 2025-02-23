import requests
import time
import pandas as pd
import mysql.connector
import psycopg2
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# ✅ 환경 변수 로드
load_dotenv()
BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com/api/v3")
BINANCE_FUTURES_URL = os.getenv("BINANCE_FUTURES_URL", "https://fapi.binance.com/fapi/v1")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "trading_data")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "ohlcv_data")
SELECTED_COINS = os.getenv("SELECTED_COINS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")
USE_MYSQL = os.getenv("USE_MYSQL") == "True"
USE_POSTGRES = os.getenv("USE_POSTGRES") == "True"
USE_MONGO = os.getenv("USE_MONGO") == "True"

class OHLCVCollector:
    def __init__(self, intervals=["1m", "5m", "15m", "1h", "4h", "1d"], limit=500, use_futures=False):
        """ ✅ 다중 코인 OHLCV 데이터 수집 클래스 """
        self.symbols = [coin.strip().upper() for coin in SELECTED_COINS]
        self.intervals = intervals
        self.limit = limit
        self.use_futures = use_futures
        self.base_url = BINANCE_FUTURES_URL if self.use_futures else BINANCE_BASE_URL

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

    def fetch_ohlcv(self, symbol, interval):
        """ ✅ Binance에서 OHLCV 데이터 수집 """
        url = f"{self.base_url}/klines"
        params = {"symbol": symbol, "interval": interval, "limit": self.limit}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            ohlcv = [{
                "timestamp": datetime.utcfromtimestamp(entry[0] / 1000),
                "symbol": symbol,
                "interval": interval,
                "open": float(entry[1]),
                "high": float(entry[2]),
                "low": float(entry[3]),
                "close": float(entry[4]),
                "volume": float(entry[5])
            } for entry in data]

            self.store_data(ohlcv)
            return ohlcv
        except requests.RequestException as e:
            print(f"🚨 [OHLCV] {symbol} {interval} 데이터 요청 실패: {e}")
            return None

    def store_data(self, data):
        """ ✅ 데이터 저장 (MongoDB, MySQL, PostgreSQL) """
        if USE_MONGO:
            self.collection.insert_many(data)

        if USE_MYSQL:
            sql = """
            INSERT INTO ohlcv_data (timestamp, symbol, interval, open, high, low, close, volume) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            for row in data:
                self.mysql_cursor.execute(sql, (
                    row["timestamp"], row["symbol"], row["interval"], row["open"],
                    row["high"], row["low"], row["close"], row["volume"]
                ))
            self.mysql_conn.commit()

        if USE_POSTGRES:
            sql = """
            INSERT INTO ohlcv_data (timestamp, symbol, interval, open, high, low, close, volume) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            for row in data:
                self.postgres_cursor.execute(sql, (
                    row["timestamp"], row["symbol"], row["interval"], row["open"],
                    row["high"], row["low"], row["close"], row["volume"]
                ))
            self.postgres_conn.commit()

    def run(self):
        """ ✅ 다중 코인 OHLCV 데이터 수집 실행 """
        for symbol in self.symbols:
            for interval in self.intervals:
                self.fetch_ohlcv(symbol, interval)

# ✅ 사용 예시
if __name__ == "__main__":
    collector = OHLCVCollector()
    collector.run()
