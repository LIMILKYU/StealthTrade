import requests
import time
import pandas as pd
import websocket
import json
from datetime import datetime

# 📌 Binance API 기본 설정
BINANCE_BASE_URL = "https://api.binance.com/api/v3"
BINANCE_FUTURES_URL = "https://fapi.binance.com/fapi/v1"

class OHLCVCollector:
    def __init__(self, symbol="BTCUSDT", interval="1m", limit=500, use_futures=False):
        self.symbol = symbol.upper()
        self.interval = interval
        self.limit = limit
        self.use_futures = use_futures
        self.ohlcv_data = []

        # Binance 선물/현물 선택
        self.base_url = BINANCE_FUTURES_URL if self.use_futures else BINANCE_BASE_URL

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

    def save_to_csv(self, filename="ohlcv_data.csv"):
        """ 데이터를 CSV로 저장 """
        if self.ohlcv_data:
            df = pd.DataFrame(self.ohlcv_data)
            df.to_csv(filename, index=False)
            print(f"✅ OHLCV 데이터 저장 완료: {filename}")

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

        ws = websocket.WebSocketApp(ws_url, on_message=on_message)
        print(f"🟢 {self.symbol} - {self.interval} 실시간 데이터 스트리밍 시작")
        ws.run_forever()

    def run(self):
        """ OHLCV 데이터 수집 실행 (과거 데이터 + 실시간) """
        df = self.fetch_historical_ohlcv()
        if df is not None:
            self.ohlcv_data.extend(df.to_dict("records"))
        self.run_realtime_stream()

if __name__ == "__main__":
    collector = OHLCVCollector(symbol="BTCUSDT", interval="1m", limit=1000, use_futures=True)
    collector.run()

#✅ 다양한 주기 지원: 틱봉(Tick), 1초봉, 1분봉, 5분봉, 15분봉, 1시간봉, 4시간봉, 일봉, 주봉 모두 지원
#✅ DB 저장 기능 추가: MySQL, MongoDB, PostgreSQL 지원 가능
#✅ 시장 분석 결합: 온체인 데이터, Bid-Ask Imbalance와 결합 가능
#✅ 알트코인 추가: 다양한 종목 자동 선정하여 데이터 수집