import csv
import logging
import os
import pymysql
import sqlite3
import pymongo
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# ✅ 환경 변수 로드
load_dotenv()

# ✅ 로깅 설정
logging.basicConfig(level=logging.INFO)

# ✅ SQLAlchemy 설정 (MySQL, SQLite)
Base = declarative_base()

class TradeRecord(Base):
    """ ✅ 거래 기록 테이블 (MySQL / SQLite) """
    __tablename__ = "trade_logs"
    timestamp = Column(DateTime, primary_key=True)
    symbol = Column(String(10))
    side = Column(String(10))
    price = Column(Float)
    quantity = Column(Float)

class TradeLogger:
    def __init__(self):
        """ ✅ 거래 기록 관리 클래스 (CSV, MySQL, SQLite, MongoDB 지원) """
        self.storage_type = os.getenv("TRADE_STORAGE", "CSV").upper()
        self.log_file = os.getenv("TRADE_LOG_FILE", "trade_log.csv")
        self.db_url = os.getenv("DATABASE_URL", "sqlite:///trade_logs.db")
        self.mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.mongo_db = os.getenv("MONGO_DB", "trading")
        self.mongo_collection = os.getenv("MONGO_COLLECTION", "trade_logs")

        if self.storage_type == "MYSQL" or self.storage_type == "SQLITE":
            self.engine = create_engine(self.db_url)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)

        elif self.storage_type == "MONGODB":
            self.mongo_client = pymongo.MongoClient(self.mongo_url)
            self.mongo_database = self.mongo_client[self.mongo_db]
            self.mongo_collection = self.mongo_database[self.mongo_collection]

        # ✅ CSV 파일이 없으면 헤더 추가
        elif self.storage_type == "CSV" and not os.path.exists(self.log_file):
            with open(self.log_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "symbol", "side", "price", "quantity"])
            logging.info(f"✅ 새로운 거래 로그 파일 생성: {self.log_file}")

    def log_trade(self, symbol, side, price, quantity):
        """ ✅ 거래 내역 기록 (CSV / MySQL / SQLite / MongoDB) """
        timestamp = datetime.now()

        if self.storage_type == "CSV":
            self._log_to_csv(timestamp, symbol, side, price, quantity)

        elif self.storage_type == "MYSQL" or self.storage_type == "SQLITE":
            self._log_to_sql_db(timestamp, symbol, side, price, quantity)

        elif self.storage_type == "MONGODB":
            self._log_to_mongodb(timestamp, symbol, side, price, quantity)

    def _log_to_csv(self, timestamp, symbol, side, price, quantity):
        """ ✅ CSV 파일에 거래 기록 저장 """
        try:
            with open(self.log_file, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, symbol, side, price, quantity])
            logging.info(f"✅ [CSV] 거래 기록: {timestamp} | {symbol} | {side} | {price} | {quantity}")
        except Exception as e:
            logging.error(f"🚨 [CSV] 거래 기록 실패: {e}")

    def _log_to_sql_db(self, timestamp, symbol, side, price, quantity):
        """ ✅ MySQL 또는 SQLite에 거래 기록 저장 """
        try:
            session = self.Session()
            new_trade = TradeRecord(timestamp=timestamp, symbol=symbol, side=side, price=price, quantity=quantity)
            session.add(new_trade)
            session.commit()
            session.close()
            logging.info(f"✅ [SQL DB] 거래 기록 저장 완료: {timestamp}, {symbol}, {side}, {price}, {quantity}")
        except Exception as e:
            logging.error(f"🚨 [SQL DB] 거래 기록 실패: {e}")

    def _log_to_mongodb(self, timestamp, symbol, side, price, quantity):
        """ ✅ MongoDB에 거래 기록 저장 """
        try:
            trade_data = {
                "timestamp": timestamp,
                "symbol": symbol,
                "side": side,
                "price": price,
                "quantity": quantity
            }
            self.mongo_collection.insert_one(trade_data)
            logging.info(f"✅ [MongoDB] 거래 기록 저장 완료: {trade_data}")
        except Exception as e:
            logging.error(f"🚨 [MongoDB] 거래 기록 실패: {e}")

# ✅ 사용 예시
if __name__ == "__main__":
    logger = TradeLogger()
    logger.log_trade("BTCUSDT", "BUY", 50000, 0.01)
