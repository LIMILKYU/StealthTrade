#✅ 미결제약정(Open Interest) 실시간 수집 (WebSocket 기반)
#✅ 과거 미결제약정 데이터 수집 (REST API 기반)
#✅ 틱 단위(Tick) & 주기별(Aggregated) 데이터 지원
#✅ CSV 파일 저장 및 DB 저장 기능 추가 가능
#✅ 시장 변동성 및 트렌드 분석과 결합 가능

import requests
import time
import pandas as pd
import websocket
import json
from datetime import datetime

# 📌 Binance Futures API URL
BINANCE_FUTURES_BASE_URL = "https://fapi.binance.com/fapi/v1"

class OpenInterestTracker:
    def __init__(self, symbol="BTCUSDT", interval="5m", limit=500):
        self.symbol = symbol.upper()
        self.interval = interval
        self.limit = limit
        self.oi_data = []

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
            print("🚨 미결제약정 데이터 요청 실패!")
            return None

    def save_to_csv(self, filename="open_interest_data.csv"):
        """ 데이터를 CSV로 저장 """
        if self.oi_data:
            df = pd.DataFrame(self.oi_data)
            df.to_csv(filename, index=False)
            print(f"✅ 미결제약정 데이터 저장 완료: {filename}")

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
            print(f"📊 실시간 OI: {oi_entry}")

        ws = websocket.WebSocketApp(ws_url, on_message=on_message)
        print(f"🟢 {self.symbol} 미결제약정 실시간 데이터 스트리밍 시작")
        ws.run_forever()

    def run(self):
        """ 미결제약정 데이터 수집 실행 (과거 데이터 + 실시간) """
        df = self.fetch_historical_open_interest()
        if df is not None:
            self.oi_data.extend(df.to_dict("records"))
        self.run_realtime_stream()

if __name__ == "__main__":
    tracker = OpenInterestTracker(symbol="BTCUSDT", interval="5m", limit=1000)
    tracker.run()

#✅ 다양한 종목 지원: BTCUSDT 외에도 ETHUSDT, SOLUSDT 등 다중 종목 분석
#✅ DB 저장 기능 추가: MySQL, MongoDB, PostgreSQL 지원 가능
#✅ 시장 변동성 분석 결합: 거래량, 가격 변동성과 함께 분석
#✅ 핵심 트레이딩 전략 연계: OI 증가 → 강한 트렌드 지속 / OI 감소 → 반전 가능성 증가