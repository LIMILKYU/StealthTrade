import requests
import logging
import os
from dotenv import load_dotenv
from config import Config

# ✅ Mock 데이터 반환 함수 추가
def get_mock_market_data():
    """ 바이낸스 API 없이 실행할 때 가짜 시장 데이터 반환 """
    return [
        {"symbol": "BTCUSDT", "quoteVolume": "100000000", "priceChangePercent": "5.0"},
        {"symbol": "ETHUSDT", "quoteVolume": "75000000", "priceChangePercent": "3.2"},
    ]

# ✅ AI 변동성 최적화 객체 생성
ai_optimizer = AIRealTimeOptimizer()

class CoinSelector:
    def __init__(self, min_volume=50000000, min_volatility=0.02, user_defined_pairs=None):
        self.api_url = "https://api.binance.com/api/v3/ticker/24hr"
        self.min_volume = min_volume
        self.min_volatility = min_volatility
        self.user_defined_pairs = user_defined_pairs or []
        self.selected_coins = []

    def filter_coins(self):
        """ ✅ AI 변동성 분석을 반영하여 변동성이 높은 코인을 자동 선정 """
        if Config.BINANCE_API_KEY is None or Config.BINANCE_SECRET_KEY is None:
            logging.warning("🚨 Binance API 없음 → Mock 데이터 사용")
            data = [
                {"symbol": "BTCUSDT", "quoteVolume": "100000000", "priceChangePercent": "5.0"},
                {"symbol": "ETHUSDT", "quoteVolume": "75000000", "priceChangePercent": "3.2"},
            ]
        else:
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

        logging.info(f"📌 최종 매매 대상 코인: {self.selected_coins}")
        return self.selected_coins
