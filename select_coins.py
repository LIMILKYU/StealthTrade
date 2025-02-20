import requests
import numpy as np
import os
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일에서 API 키 및 설정값 가져오기)
load_dotenv()

class CoinSelector:
    def __init__(self):
        self.binance_base_url = os.getenv("BINANCE_BASE_URL", "https://api.binance.com/api/v3/ticker/24hr")
        self.binance_oi_url = os.getenv("BINANCE_OI_URL", "https://fapi.binance.com/fapi/v1/openInterest")
        self.binance_funding_url = os.getenv("BINANCE_FUNDING_URL", "https://fapi.binance.com/fapi/v1/premiumIndex")
        self.glassnode_api_key = os.getenv("GLASSNODE_API_KEY")  # ✅ 온체인 데이터 API 키

    def fetch_top_volatile_coins(self, top_n=5):
        """ 변동성 + 거래량 + 유동성을 고려한 최적의 코인 자동 선택 """
        response = requests.get(self.binance_base_url)
        if response.status_code != 200:
            print("🚨 [API 오류] 변동성 데이터 조회 실패")
            return []

        tickers = response.json()
        volatility_data = []

        for ticker in tickers:
            if ticker["symbol"].endswith("USDT"):  # USDT 마켓 필터링
                price_change = abs(float(ticker["priceChangePercent"]))  # 24시간 변동성
                volume = float(ticker["quoteVolume"])  # 거래대금
                spread = self.fetch_bid_ask_spread(ticker["symbol"])  # 호가 스프레드
                oi = self.fetch_open_interest(ticker["symbol"])  # 미결제약정(OI)
                funding_rate = self.fetch_funding_rate(ticker["symbol"])  # 펀딩비
                whale_activity = self.fetch_whale_activity(ticker["symbol"])  # 고래 매매 분석

                # ✅ 변동성 + 거래량 + 유동성 + OI + 펀딩비 + 고래 매매 데이터를 반영한 점수 계산
                score = (price_change * (volume ** 0.5) / (spread + 1e-9)) + (oi * 0.1) + (funding_rate * 10) + (whale_activity * 5)
                volatility_data.append((ticker["symbol"], score))

        # ✅ 상위 N개 코인 선택
        volatility_data.sort(key=lambda x: x[1], reverse=True)
        return [symbol for symbol, _ in volatility_data[:top_n]]

    def fetch_bid_ask_spread(self, symbol):
        """ 유동성을 평가하기 위한 Bid-Ask 스프레드 계산 """
        url = f"{os.getenv('BINANCE_ORDER_BOOK_URL', 'https://api.binance.com/api/v3/depth')}?symbol={symbol}&limit=5"
        response = requests.get(url)
        if response.status_code == 200:
            order_book = response.json()
            best_bid = float(order_book["bids"][0][0])
            best_ask = float(order_book["asks"][0][0])
            spread = abs(best_ask - best_bid) / best_bid
            return spread
        return 0.01  # 기본값 (스프레드가 높으면 유동성이 낮음)

    def fetch_open_interest(self, symbol):
        """ 미결제약정(OI) 데이터 가져오기 """
        response = requests.get(f"{self.binance_oi_url}?symbol={symbol}")
        if response.status_code == 200:
            oi_data = response.json()
            return float(oi_data["openInterest"])
        return 0

    def fetch_funding_rate(self, symbol):
        """ 펀딩비 데이터 가져오기 """
        response = requests.get(f"{self.binance_funding_url}?symbol={symbol}")
        if response.status_code == 200:
            funding_data = response.json()
            return float(funding_data["lastFundingRate"])
        return 0

    def fetch_whale_activity(self, symbol):
        """ 온체인 데이터를 기반으로 고래 매매 분석 """
        url = f"https://api.glassnode.com/v1/metrics/transactions/transfers_volume_whales"
        params = {"a": symbol.replace("USDT", ""), "api_key": self.glassnode_api_key}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            whale_data = response.json()
            whale_volume = whale_data[-1]["v"]  # 최근 고래 거래량
            return whale_volume / 1e6  # 값 정규화
        return 0

    def should_switch_coin(self, current_coin):
        """ 매매 완료 후 코인을 변경할지 판단 """
        top_coins = self.fetch_top_volatile_coins(top_n=5)

        if current_coin in top_coins:
            print(f"✅ [코인 유지] 현재 코인({current_coin}) 변동성 상위권 유지")
            return current_coin  # 현재 코인 유지
        else:
            new_coin = top_coins[0]  # 가장 변동성 높은 코인으로 변경
            print(f"🔄 [코인 교체] {current_coin} → {new_coin}")
            return new_coin

if __name__ == "__main__":
    selector = CoinSelector()
    top_coins = selector.fetch_top_volatile_coins()
    print(f"🚀 [변동성 높은 코인 TOP 5]: {top_coins}")

    current_coin = "BTCUSDT"
    new_coin = selector.should_switch_coin(current_coin)
    print(f"🔄 [최종 선택된 코인]: {new_coin}")
