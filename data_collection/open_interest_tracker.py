import requests
import time
import json
import pandas as pd
import websocket
import mysql.connector
import psycopg2
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from coin_selector import SELECTED_COIN  # 📌 `coin_selector.py`에서 선택된 코인 가져오기

# 환경 변수 로드 (.env 파일에서 API 및 DB 설정 불러오기)
load_dotenv()

BINANCE_FUTURES_BASE_URL = os.getenv("BINANCE_FUTURES_BASE_URL", "https://fapi.binance.com/fapi/v1")

class OpenInterestTracker:
    def __init__(self, interval="5m", limit=500, save_db=True):
        self.symbol = SELECTED_COIN.upper()  # ✅ `coin_selector.py`에서 선택된 코인 적용
        self.interval = interval
        self.limit = limit
        self.save_db = save_db
        self.oi_data = []

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
            self.mongo_collection = self.mongo_db["open_interest"]

    def fetch_historical_open_interest(self):
        """ 바이낸스에서 과거 미결제약정(Open Interest) 데이터 수집 """
        url = f"{BINANCE_FUTURES_BASE_URL}/openInterestHist"
        params = {
            "symbol": self.symbol,
            "period": self.interval,
            "limit": self.limit,
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["openInterest"] = df["sumOpenInterest"]
            df["openInterestValue"] = df["sumOpenInterestValue"]
            df = df[["timestamp", "openInterest", "openInterestValue"]]
            print(f"✅ {self.symbol} - {self.interval} 미결제약정 데이터 수집 완료 ({len(df)}개)")
            return df
        else:
            print(f"🚨 {self.symbol} 미결제약정 데이터 요청 실패!")
            return None

    def save_to_db(self, df):
        """ 미결제약정 데이터를 MySQL, PostgreSQL, MongoDB에 저장 """
        if df is None or not self.save_db:
            return

        for _, row in df.iterrows():
            record = (row["timestamp"], row["openInterest"], row["openInterestValue"])

            if self.use_mysql:
                query = "INSERT INTO open_interest (timestamp, open_interest, open_interest_value) VALUES (%s, %s, %s)"
                self.mysql_cursor.execute(query, record)
                self.mysql_conn.commit()

            if self.use_postgres:
                query = "INSERT INTO open_interest (timestamp, open_interest, open_interest_value) VALUES (%s, %s, %s)"
                self.postgres_cursor.execute(query, record)
                self.postgres_conn.commit()

            if self.use_mongo:
                self.mongo_collection.insert_one({
                    "timestamp": row["timestamp"],
                    "open_interest": row["openInterest"],
                    "open_interest_value": row["openInterestValue"]
                })

        print(f"✅ {self.symbol} 미결제약정 데이터 DB 저장 완료!")

    def save_to_csv(self, filename="open_interest_data.csv"):
        """ 미결제약정 데이터를 CSV 파일로 저장 """
        if self.oi_data:
            df = pd.DataFrame(self.oi_data)
            df.to_csv(filename, index=False)
            print(f"✅ {self.symbol} 미결제약정 데이터 저장 완료: {filename}")

    def run_realtime_stream(self):
        """ WebSocket을 이용한 실시간 미결제약정 데이터 스트리밍 """
        ws_url = f"wss://fstream.binance.com/ws/{self.symbol.lower()}@openInterest"

        def on_message(ws, message):
            data = json.loads(message)
            oi_entry = {
                "timestamp": datetime.utcnow(),
                "openInterest": float(data["openInterest"]),
                "openInterestValue": float(data["openInterestValue"]),
            }
            self.oi_data.append(oi_entry)
            print(f"📊 [{self.symbol}] 실시간 OI: {oi_entry}")

            # 실시간 데이터도 DB에 저장
            self.save_to_db(pd.DataFrame([oi_entry]))

        ws = websocket.WebSocketApp(ws_url, on_message=on_message)
        print(f"🟢 {self.symbol} 미결제약정 실시간 데이터 스트리밍 시작")
        ws.run_forever()

    def run(self):
        """ 미결제약정 데이터 수집 실행 (과거 데이터 + 실시간) """
        df = self.fetch_historical_open_interest()
        if df is not None:
            self.oi_data.extend(df.to_dict("records"))
            self.save_to_db(df)

        self.run_realtime_stream()

if __name__ == "__main__":
    tracker = OpenInterestTracker(interval="5m", limit=1000, save_db=True)
    tracker.run()
