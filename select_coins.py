import requests
import numpy as np
import pandas as pd
from config import BINANCE_BASE_URL, NUM_COINS_TO_TRADE, AUTO_SELECT_COIN, USER_SELECTED_COINS

def fetch_top_coins():
    """ 바이낸스에서 상위 거래량 코인 가져오기 """
    url = f"{BINANCE_BASE_URL}/api/v3/ticker/24hr"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        # USDT 페어만 필터링
        df = df[df["symbol"].str.endswith("USDT")]

        # 🔹 거래량(quoteVolume), 변동성(high-low), 거래대금(weightedAvgPrice) 기준 정렬
        df["volatility"] = df["highPrice"].astype(float) - df["lowPrice"].astype(float)
        df["trade_value"] = df["quoteVolume"].astype(float)
        
        # 종합 점수 계산 (거래대금 * 변동성)
        df["score"] = df["trade_value"] * df["volatility"]
        df = df.sort_values("score", ascending=False)

        # 상위 NUM_COINS_TO_TRADE 개 코인 선택
        return df["symbol"].head(NUM_COINS_TO_TRADE).tolist()
    else:
        print("❌ 코인 리스트 가져오기 실패!")
        return []

def get_selected_coins():
    """ 사용자가 선택한 코인 또는 자동 선정 코인 반환 """
    if AUTO_SELECT_COIN:
        selected_coins = fetch_top_coins()
    else:
        selected_coins = USER_SELECTED_COINS

    print(f"✅ 매매할 코인: {selected_coins}")
    return selected_coins
