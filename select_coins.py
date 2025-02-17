import requests
import logging
import os
from dotenv import load_dotenv
from backend.t_rpc_client import tRPCClient

# .env 파일 로드
load_dotenv()

class CoinSelector:
    def __init__(self, min_volume=50000000, min_volatility=0.02, user_defined_pairs=None):
        self.api_url = "https://api.binance.com/api/v3/ticker/24hr"
        self.min_volume = min_volume
        self.min_volatility = min_volatility
        self.user_defined_pairs = user_defined_pairs or []
        self.selected_coins = []
        self.trpc_client = tRPCClient(os.getenv("TRPC_API_URL"))

    def filter_coins(self):
        """ 변동성이 높은 코인을 자동으로 선정 """
        response = requests.get(self.api_url)
        if response.status_code != 200:
            logging.error("❌ 시장 데이터 가져오기 실패")
            return []

        data = response.json()
        for coin in data:
            symbol = coin["symbol"]
            volume = float(coin["quoteVolume"])
            price_change = abs(float(coin["priceChangePercent"])) / 100  

            if volume > self.min_volume and price_change > self.min_volatility and symbol.endswith("USDT"):
                self.selected_coins.append(symbol)

        self.selected_coins.extend(self.user_defined_pairs)
        logging.info(f"📌 최종 매매 대상 코인: {self.selected_coins}")

        # tRPC API를 통해 프론트엔드 업데이트
        self.trpc_client.update_trade_data({"selected_coins": self.selected_coins})

        return self.selected_coins
