import requests
import logging
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class tRPCClient:
    def __init__(self):
        """ tRPC API 클라이언트 - 프론트엔드 대시보드와 데이터 동기화 """
        self.trpc_url = os.getenv("TRPC_API_URL")
        logging.basicConfig(level=logging.INFO)

    def update_trade_data(self, trade_data: dict):
        """ 주문 체결 후 프론트엔드에 실시간 업데이트 """
        try:
            response = requests.post(f"{self.trpc_url}/updateTrade", json=trade_data)

            if response.status_code == 200:
                logging.info(f"✅ tRPC 업데이트 성공: {trade_data}")
            else:
                logging.error(f"❌ tRPC 업데이트 실패! 응답 코드: {response.status_code}, 메시지: {response.text}")

        except requests.exceptions.RequestException as e:
            logging.error(f"⚠️ tRPC 요청 실패: {e}")

    def update_market_data(self, market_data: dict):
        """ 시장 변동성 데이터 업데이트 """
        try:
            response = requests.post(f"{self.trpc_url}/updateMarket", json=market_data)

            if response.status_code == 200:
                logging.info(f"✅ 시장 데이터 업데이트 성공: {market_data}")
            else:
                logging.error(f"❌ 시장 데이터 업데이트 실패: {response.status_code}, 메시지: {response.text}")

        except requests.exceptions.RequestException as e:
            logging.error(f"⚠️ 시장 데이터 요청 실패: {e}")

# 사용 예시
if __name__ == "__main__":
    trpc_client = tRPCClient()

    sample_trade_data = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": 0.01,
        "price": 45000.0,
        "status": "FILLED"
    }
    trpc_client.update_trade_data(sample_trade_data)

    sample_market_data = {
        "ATR": 0.025,
        "bollinger_width": 0.015,
        "volatility": 0.03
    }
    trpc_client.update_market_data(sample_market_data)
