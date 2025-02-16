import requests
import time
import json
import pandas as pd
from datetime import datetime

# 📌 CryptoQuant API 키 (사용자 API 키 입력 필요)
CRYPTOQUANT_API_KEY = "YOUR_CRYPTOQUANT_API_KEY"
CRYPTOQUANT_BASE_URL = "https://api.cryptoquant.com/v1"

# 📌 Glassnode API 키 (대체 API, 필요 시 활성화)
GLASSNODE_API_KEY = "YOUR_GLASSNODE_API_KEY"
GLASSNODE_BASE_URL = "https://api.glassnode.com/v1/metrics"

class OnchainDataFetcher:
    def __init__(self, symbol="BTC"):
        self.symbol = symbol
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {CRYPTOQUANT_API_KEY}"})
        self.data_log = []

    def fetch_exchange_flows(self):
        """ 거래소 유입/유출량 데이터 수집 """
        url = f"{CRYPTOQUANT_BASE_URL}/btc/exchange-flows"
        params = {"exchange": "all", "interval": "1h"}
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            latest = data["result"][-1]  # 최신 데이터
            netflow = latest["netflow"]  # 순유입량
            inflow = latest["inflow"]  # 유입량
            outflow = latest["outflow"]  # 유출량
            
            print(f"🔹 거래소 유입량: {inflow:.2f} BTC | 유출량: {outflow:.2f} BTC | 순유입: {netflow:.2f} BTC")
            return {"timestamp": latest["timestamp"], "inflow": inflow, "outflow": outflow, "netflow": netflow}
        
        print("🚨 거래소 유입/유출 데이터 요청 실패!")
        return None

    def fetch_open_interest(self):
        """ 미결제약정(Open Interest) 데이터 수집 """
        url = f"{CRYPTOQUANT_BASE_URL}/btc/open-interest"
        params = {"exchange": "all", "interval": "1h"}
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            latest = data["result"][-1]
            open_interest = latest["open_interest"]
            
            print(f"📊 미결제약정 (Open Interest): {open_interest:.2f} BTC")
            return {"timestamp": latest["timestamp"], "open_interest": open_interest}
        
        print("🚨 미결제약정 데이터 요청 실패!")
        return None

    def fetch_active_addresses(self):
        """ 활성 주소 수 데이터 수집 (Glassnode API 사용) """
        url = f"{GLASSNODE_BASE_URL}/addresses/active_count"
        params = {"a": "BTC", "api_key": GLASSNODE_API_KEY}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            latest = data[-1]  # 최신 데이터
            active_addresses = latest["value"]
            
            print(f"📌 활성 주소 수: {active_addresses}")
            return {"timestamp": latest["t"], "active_addresses": active_addresses}

        print("🚨 활성 주소 수 데이터 요청 실패!")
        return None

    def save_to_csv(self, filename="onchain_data.csv"):
        """ 온체인 데이터를 CSV 파일로 저장 """
        if self.data_log:
            df = pd.DataFrame(self.data_log)
            df.to_csv(filename, index=False)
            print(f"✅ 온체인 데이터 저장 완료: {filename}")

    def run(self, interval=10):
        """ 온체인 데이터 실시간 수집 및 저장 """
        while True:
            print(f"\n🟢 [{datetime.now()}] 온체인 데이터 수집 시작")
            exchange_data = self.fetch_exchange_flows()
            oi_data = self.fetch_open_interest()
            active_addr_data = self.fetch_active_addresses()
            
            if exchange_data and oi_data and active_addr_data:
                combined_data = {**exchange_data, **oi_data, **active_addr_data}
                self.data_log.append(combined_data)
                print("📈 온체인 데이터 업데이트 완료!")

            if len(self.data_log) % 10 == 0:
                self.save_to_csv()

            time.sleep(interval)

if __name__ == "__main__":
    fetcher = OnchainDataFetcher()
    fetcher.run()
