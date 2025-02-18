import requests
import json
import time
import os
import hmac
import hashlib
from config import Config

# ✅ 변경된 코드 (Mock 데이터 추가)
def get_mock_binance_response():
    """ 바이낸스 API 없이 실행할 때 가짜 응답 반환 """
    return {
        "symbol": "BTCUSDT",
        "price": "45000.00",
        "orderId": 123456,
        "status": "FILLED"
    }

def place_order(symbol, order_type):
    """ 특정 코인에 대해 매매 주문 실행 """
    
    # ✅ 변경된 코드 (Paper Trading 모드 추가)
    if Config.PAPER_TRADING:
        print(f"📌 [Paper Trading] {order_type} 주문 실행: {symbol}")
        return {
            "symbol": symbol,
            "price": "45000.00",
            "orderId": 999999,
            "status": "TEST_MODE"
        }

    # ✅ 변경된 코드 (API 키가 없을 경우 Mock 데이터 반환)
    if Config.BINANCE_API_KEY is None or Config.BINANCE_SECRET_KEY is None:
        print("🚨 [테스트 모드] 바이낸스 API 없이 실행 중")
        return get_mock_binance_response()

    # 🔴 기존 코드 (API 요청 부분)
    # url = f"{Config.BINANCE_BASE_URL}/api/v3/order"
    # headers = {"X-MBX-APIKEY": Config.BINANCE_API_KEY}
    # params = {
    #     "symbol": symbol,
    #     "side": order_type,
    #     "type": "MARKET",
    #     "quantity": 0.01,
    #     "timestamp": int(time.time() * 1000),
    # }
    
    # ✅ 변경된 코드 (API가 있을 경우에만 실행)
    if Config.BINANCE_API_KEY and Config.BINANCE_SECRET_KEY:
        try:
            response = requests.post(url, headers=headers, params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"❌ API 요청 실패: {e}")
            return None

if __name__ == "__main__":
    print(place_order("BTCUSDT", "BUY"))  # 바이낸스 API 없이 실행 가능
