import requests
import time
import pandas as pd
import websocket
import json
import mysql.connector
import psycopg2
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from coin_selector import SELECTED_COIN  # 📌 `coin_selector.py`에서 코인 선택 변수 가져오기

# 환경 변수 로드 (.env 파일에서 API 키 및 설정값 가져오기)
load_dotenv()

BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com/api/v3")
BINANCE_FUTURES_URL = os.getenv("BINANCE_FUTURES_URL", "https://fapi.binance.com/fapi/v1")

class OHLCVCollector:
    def __init__(self, interval="1m", limit=500, use_futures=False, save_db=True):
        self.symbol = SELECTED_COIN.upper()  # ✅ `coin_selector.py`에서 선택된 코인 적용
        self.interval = interval
        self.limit = limit
        self.use_futures = use_futures
        self.save_db = save_db
        self.ohlcv_data = []

        # Binance 선물/현물 선택
        self.base_url = BINANCE_FUTURES_URL if self.use_futures else BINANCE_BASE_URL

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
            self.mongo_collection = self.mongo_db["ohlcv"]

    def fetch_historical_ohlcv(self):
        """ 바이낸스에서 과거 OHLCV 데이터 수집 """
        url = f"{self.base_url}/klines"
        params = {
            "symbol": self.symbol,
            "interval": self.interval,
            "limit": self.limit,
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", 
                                             "quote_asset_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df[["timestamp", "open", "high", "low", "close", "volume"]]
            print(f"✅ {self.symbol} - {self.interval} 데이터 수집 완료 ({len(df)}개)")
            return df
        else:
            print("🚨 OHLCV 데이터 요청 실패!")
            return None

    def save_to_db(self, df):
        """ OHLCV 데이터를 MySQL, PostgreSQL, MongoDB에 저장 """
        if df is None or not self.save_db:
            return

        for _, row in df.iterrows():
            record = (row["timestamp"], row["open"], row["high"], row["low"], row["close"], row["volume"])

            if self.use_mysql:
                query = "INSERT INTO ohlcv (timestamp, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s)"
                self.mysql_cursor.execute(query, record)
                self.mysql_conn.commit()

            if self.use_postgres:
                query = "INSERT INTO ohlcv (timestamp, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s)"
                self.postgres_cursor.execute(query, record)
                self.postgres_conn.commit()

            if self.use_mongo:
                self.mongo_collection.insert_one({
                    "timestamp": row["timestamp"],
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"]
                })

        print(f"✅ {self.symbol} 데이터 DB 저장 완료!")

    def fetch_onchain_data(self):
        """ 온체인 데이터 분석 (거래소 입출금 및 고래 활동 분석) """
        url = f"https://api.glassnode.com/v1/metrics/exchange/flows"
        params = {"a": self.symbol, "api_key": os.getenv("GLASSNODE_API_KEY")}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {self.symbol} 온체인 데이터 수집 완료!")
            return data
        else:
            print("🚨 온체인 데이터 요청 실패!")
            return None

    def run_realtime_stream(self):
        """ WebSocket을 이용한 실시간 OHLCV 데이터 스트리밍 """
        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol.lower()}@kline_{self.interval}"
        
        def on_message(ws, message):
            data = json.loads(message)
            kline = data["k"]["t"], data["k"]["o"], data["k"]["h"], data["k"]["l"], data["k"]["c"], data["k"]["v"]
            ohlcv_entry = {
                "timestamp": datetime.fromtimestamp(kline[0] / 1000),
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5])
            }
            self.ohlcv_data.append(ohlcv_entry)
            print(f"📊 실시간 OHLCV: {ohlcv_entry}")

            # 실시간 데이터도 DB에 저장
            self.save_to_db(pd.DataFrame([ohlcv_entry]))

        ws = websocket.WebSocketApp(ws_url, on_message=on_message)
        print(f"🟢 {self.symbol} - {self.interval} 실시간 데이터 스트리밍 시작")
        ws.run_forever()

    def run(self):
        """ OHLCV 데이터 수집 실행 (과거 데이터 + 실시간 + 온체인 분석) """
        df = self.fetch_historical_ohlcv()
        if df is not None:
            self.ohlcv_data.extend(df.to_dict("records"))
            self.save_to_db(df)

        self.fetch_onchain_data()  # ✅ 온체인 데이터 분석 추가
        self.run_realtime_stream()

if __name__ == "__main__":
    collector = OHLCVCollector(interval="1m", limit=1000, use_futures=True, save_db=True)
    collector.run()
