import requests
import time
import json
import logging
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient

# ✅ 환경 변수 로드
load_dotenv()
CRYPTOQUANT_API_KEY = os.getenv("CRYPTOQUANT_API_KEY")
GLASSNODE_API_KEY = os.getenv("GLASSNODE_API_KEY")
CRYPTOQUANT_BASE_URL = os.getenv("CRYPTOQUANT_BASE_URL", "https://api.cryptoquant.com/v1")
GLASSNODE_BASE_URL = os.getenv("GLASSNODE_BASE_URL", "https://api.glassnode.com/v1")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "trading_data")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "onchain_data")

# ✅ 로깅 설정
logging.basicConfig(level=logging.INFO)

class OnchainDataFetcher:
    def __init__(self, symbol="BTC"):
        """ ✅ 온체인 데이터 수집 클래스 """
        self.symbol = symbol.upper()
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {CRYPTOQUANT_API_KEY}"})
        self.mongo_client = MongoClient(MONGO_URL)
        self.db = self.mongo_client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION]

    def fetch_exchange_flows(self):
        """ ✅ 거래소 유입/유출량 데이터 수집 (CryptoQuant API) """
        url = f"{CRYPTOQUANT_BASE_URL}/{self.symbol.lower()}/exchange-flows"
        params = {"exchange": "all", "interval": "1h"}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            latest = data["result"][-1]
            result = {
                "timestamp": datetime.utcfromtimestamp(latest["timestamp"]),
                "symbol": self.symbol,
                "inflow": latest["inflow"],
                "outflow": latest["outflow"],
                "netflow": latest["netflow"]
            }
            self.store_data(result)
            logging.info(f"✅ [거래소 유입량] {result}")
            return result
        except requests.RequestException as e:
            logging.error(f"🚨 [거래소 유입량] API 요청 실패: {e}")
            return None

    def fetch_open_interest(self):
        """ ✅ 미결제약정(Open Interest) 데이터 수집 """
        url = f"{CRYPTOQUANT_BASE_URL}/{self.symbol.lower()}/open-interest"
        params = {"exchange": "all", "interval": "1h"}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            latest = data["result"][-1]
            result = {
                "timestamp": datetime.utcfromtimestamp(latest["timestamp"]),
                "symbol": self.symbol,
                "open_interest": latest["open_interest"]
            }
            self.store_data(result)
            logging.info(f"✅ [미결제약정] {result}")
            return result
        except requests.RequestException as e:
            logging.error(f"🚨 [미결제약정] API 요청 실패: {e}")
            return None

    def store_data(self, data):
        """ ✅ 데이터 저장 (MongoDB) """
        try:
            self.collection.insert_one(data)
            logging.info(f"✅ [MongoDB 저장 완료] {data}")
        except Exception as e:
            logging.error(f"🚨 [MongoDB 저장 실패] {e}")

# ✅ 사용 예시
if __name__ == "__main__":
    fetcher = OnchainDataFetcher("BTC")
    fetcher.fetch_exchange_flows()
    fetcher.fetch_open_interest()
