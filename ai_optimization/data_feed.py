# 실시간 시장 데이터를 AI 최적화 시스템으로 전송
# API/WebSocket에서 데이터를 받아 AI 모델이 학습하도록 제공

import requests
import pandas as pd
import logging

class DataFeed:
    def __init__(self, api_url: str):
        """
        :param api_url: 실시간 데이터 API 주소
        """
        self.api_url = api_url
        logging.basicConfig(level=logging.INFO)

    def get_market_data(self):
        """ 실시간 시장 데이터 가져오기 """
        response = requests.get(self.api_url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            return df
        else:
            logging.error(f"🚨 Failed to fetch market data: {response.text}")
            return None

# 사용 예시
if __name__ == "__main__":
    data_feed = DataFeed("https://api.binance.com/api/v3/ticker/24hr")
    df = data_feed.get_market_data()
    print(df.head())
