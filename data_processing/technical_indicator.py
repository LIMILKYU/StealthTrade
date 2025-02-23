import numpy as np
import pandas as pd
import talib
from pymongo import MongoClient
import mysql.connector
import psycopg2
from dotenv import load_dotenv
import os

# ✅ 환경 변수 로드
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "trading_data")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "technical_indicators")
SELECTED_COINS = os.getenv("SELECTED_COINS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")
USE_MYSQL = os.getenv("USE_MYSQL") == "True"
USE_POSTGRES = os.getenv("USE_POSTGRES") == "True"
USE_MONGO = os.getenv("USE_MONGO") == "True"

class TechnicalIndicators:
    def __init__(self, df, symbol):
        """
        기술적 분석 지표 계산 클래스
        :param df: OHLCV 데이터
        :param symbol: 코인 심볼 (예: BTCUSDT)
        """
        self.df = df.copy()
        self.symbol = symbol

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

    def calculate_sma(self, period=20):
        """ 단순 이동평균선 (SMA) 계산 """
        self.df[f"SMA_{period}"] = self.df["close"].rolling(window=period).mean()

    def calculate_ema(self, period=20):
        """ 지수 이동평균선 (EMA) 계산 """
        self.df[f"EMA_{period}"] = talib.EMA(self.df["close"], timeperiod=period)

    def calculate_vwap(self):
        """ 거래량 가중 평균 가격 (VWAP) 계산 """
        self.df["VWAP"] = (self.df["close"] * self.df["volume"]).cumsum() / self.df["volume"].cumsum()

    def calculate_atr(self, period=14):
        """ 평균 진폭 범위 (ATR) 계산 """
        self.df["ATR"] = talib.ATR(self.df["high"], self.df["low"], self.df["close"], timeperiod=period)

    def calculate_rsi(self, period=14):
        """ 상대 강도 지수 (RSI) 계산 """
        self.df["RSI"] = talib.RSI(self.df["close"], timeperiod=period)

    def calculate_macd(self):
        """ 이동평균 수렴·확산지수 (MACD) 계산 """
        self.df["MACD"], self.df["MACD_Signal"], self.df["MACD_Hist"] = talib.MACD(
            self.df["close"], fastperiod=12, slowperiod=26, signalperiod=9
        )

    def calculate_bollinger_bands(self, period=20):
        """ 볼린저 밴드 계산 """
        self.df["Upper_BB"], self.df["Middle_BB"], self.df["Lower_BB"] = talib.BBANDS(
            self.df["close"], timeperiod=period, nbdevup=2, nbdevdn=2, matype=0
        )

    def calculate_obv(self):
        """ 거래량 기반 지표 - OBV (On-Balance Volume) """
        self.df["OBV"] = talib.OBV(self.df["close"], self.df["volume"])

    def store_features(self):
        """ 특성 저장 (MongoDB, MySQL, PostgreSQL) """
        features = self.df.to_dict(orient="records")

        if USE_MONGO:
            self.collection.insert_many(features)

        if USE_MYSQL:
            sql = """
            INSERT INTO technical_indicators (timestamp, symbol, SMA_20, EMA_20, VWAP, ATR, RSI, MACD, MACD_Signal, MACD_Hist, Upper_BB, Middle_BB, Lower_BB, OBV) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            for feature in features:
                self.mysql_cursor.execute(sql, (
                    feature["timestamp"], feature["symbol"], feature["SMA_20"], feature["EMA_20"], feature["VWAP"], 
                    feature["ATR"], feature["RSI"], feature["MACD"], feature["MACD_Signal"], feature["MACD_Hist"],
                    feature["Upper_BB"], feature["Middle_BB"], feature["Lower_BB"], feature["OBV"]
                ))
            self.mysql_conn.commit()

        if USE_POSTGRES:
            sql = """
            INSERT INTO technical_indicators (timestamp, symbol, SMA_20, EMA_20, VWAP, ATR, RSI, MACD, MACD_Signal, MACD_Hist, Upper_BB, Middle_BB, Lower_BB, OBV) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            for feature in features:
                self.postgres_cursor.execute(sql, (
                    feature["timestamp"], feature["symbol"], feature["SMA_20"], feature["EMA_20"], feature["VWAP"], 
                    feature["ATR"], feature["RSI"], feature["MACD"], feature["MACD_Signal"], feature["MACD_Hist"],
                    feature["Upper_BB"], feature["Middle_BB"], feature["Lower_BB"], feature["OBV"]
                ))
            self.postgres_conn.commit()

    def process(self):
        """ 기술적 지표 계산 및 저장 """
        self.calculate_sma(20)
        self.calculate_ema(20)
        self.calculate_vwap()
        self.calculate_atr(14)
        self.calculate_rsi(14)
        self.calculate_macd()
        self.calculate_bollinger_bands(20)
        self.calculate_obv()
        self.store_features()

# ✅ 사용 예시
if __name__ == "__main__":
    df = pd.read_csv("ohlcv_data.csv")  # OHLCV 데이터 로드
    symbol = "BTCUSDT"  # 예시 심볼
    technical_indicator = TechnicalIndicators(df, symbol)
    technical_indicator.process()
