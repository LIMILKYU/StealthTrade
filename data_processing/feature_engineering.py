import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
from sklearn.preprocessing import MinMaxScaler
import os
from pymongo import MongoClient
import mysql.connector
import psycopg2
from dotenv import load_dotenv

# ✅ 환경 변수 로드
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "trading_data")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "feature_data")
SELECTED_COINS = os.getenv("SELECTED_COINS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")
USE_MYSQL = os.getenv("USE_MYSQL") == "True"
USE_POSTGRES = os.getenv("USE_POSTGRES") == "True"
USE_MONGO = os.getenv("USE_MONGO") == "True"

class FeatureEngineering:
    def __init__(self, df, symbol):
        """ 
        머신러닝 특성 엔지니어링 클래스
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

    def add_basic_stats(self):
        """ 기본 통계 특성 추가 (평균, 중앙값, 표준편차 등) """
        self.df["price_mean"] = self.df["close"].rolling(window=10).mean()
        self.df["price_median"] = self.df["close"].rolling(window=10).median()
        self.df["price_std"] = self.df["close"].rolling(window=10).std()
        self.df["price_max"] = self.df["close"].rolling(window=10).max()
        self.df["price_min"] = self.df["close"].rolling(window=10).min()

    def add_volatility_features(self):
        """ 변동성 관련 특성 추가 (ATR, 볼린저 밴드) """
        atr = AverageTrueRange(high=self.df["high"], low=self.df["low"], close=self.df["close"])
        self.df["ATR"] = atr.average_true_range()

        bb = BollingerBands(close=self.df["close"], window=20, window_dev=2)
        self.df["BB_High"] = bb.bollinger_hband()
        self.df["BB_Low"] = bb.bollinger_lband()
        self.df["BB_Width"] = bb.bollinger_wband()

    def add_momentum_features(self):
        """ 모멘텀 관련 특성 추가 (RSI, MACD, 모멘텀) """
        self.df["RSI"] = RSIIndicator(close=self.df["close"], window=14).rsi()
        self.df["Momentum"] = self.df["close"].diff(5)

        macd = MACD(close=self.df["close"], window_slow=26, window_fast=12, window_sign=9)
        self.df["MACD"] = macd.macd()
        self.df["MACD_Signal"] = macd.macd_signal()

    def store_features(self):
        """ 특성 저장 (MongoDB, MySQL, PostgreSQL) """
        features = self.df.to_dict(orient="records")

        if USE_MONGO:
            self.collection.insert_many(features)

        if USE_MYSQL:
            sql = """
            INSERT INTO feature_data (timestamp, symbol, price_mean, price_median, price_std, price_max, price_min, ATR, BB_High, BB_Low, BB_Width, RSI, Momentum, MACD, MACD_Signal) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            for feature in features:
                self.mysql_cursor.execute(sql, (
                    feature["timestamp"], feature["symbol"], feature["price_mean"], feature["price_median"],
                    feature["price_std"], feature["price_max"], feature["price_min"], feature["ATR"], 
                    feature["BB_High"], feature["BB_Low"], feature["BB_Width"], feature["RSI"], feature["Momentum"], 
                    feature["MACD"], feature["MACD_Signal"]
                ))
            self.mysql_conn.commit()

        if USE_POSTGRES:
            sql = """
            INSERT INTO feature_data (timestamp, symbol, price_mean, price_median, price_std, price_max, price_min, ATR, BB_High, BB_Low, BB_Width, RSI, Momentum, MACD, MACD_Signal) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            for feature in features:
                self.postgres_cursor.execute(sql, (
                    feature["timestamp"], feature["symbol"], feature["price_mean"], feature["price_median"],
                    feature["price_std"], feature["price_max"], feature["price_min"], feature["ATR"], 
                    feature["BB_High"], feature["BB_Low"], feature["BB_Width"], feature["RSI"], feature["Momentum"], 
                    feature["MACD"], feature["MACD_Signal"]
                ))
            self.postgres_conn.commit()

    def process(self):
        """ 특성 공학 프로세스 실행 """
        self.add_basic_stats()
        self.add_volatility_features()
        self.add_momentum_features()
        self.store_features()

# ✅ 사용 예시
if __name__ == "__main__":
    # 예시 데이터프레임 로드 (OHLCV 데이터)
    df = pd.read_csv("ohlcv_data.csv")  # OHLCV 데이터를 파일로부터 로드
    symbol = "BTCUSDT"  # 예시 심볼
    feature_engineer = FeatureEngineering(df, symbol)
    feature_engineer.process()
