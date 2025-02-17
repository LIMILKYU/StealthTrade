# 실시간 가격 데이터를 수집하여 AI 모델 학습에 제공하는 코드
import requests
import json
import time
import pandas as pd
from config import BINANCE_BASE_URL, TRADE_SYMBOL

def fetch_market_data():
    """ 바이낸스에서 실시간 시장 데이터를 가져옴 """
    url = f"{BINANCE_BASE_URL}/api/v3/klines?symbol={TRADE_SYMBOL}&interval=1m&limit=50"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 데이터 가져오기 실패: {response.text}")
        return None

def save_data_to_csv(data, filename="market_data.csv"):
    """ 데이터를 CSV 파일로 저장 """
    df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close", "volume"])
    df.to_csv(filename, index=False)
    print("✅ 실시간 데이터 저장 완료!")

if __name__ == "__main__":
    market_data = fetch_market_data()
    if market_data:
        save_data_to_csv(market_data)
