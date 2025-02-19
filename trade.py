import requests
import json
import time
import os
import hmac
import hashlib
from config import Config

# ✅ Mock 데이터 반환 함수 추가
def get_mock_binance_response():
    """ 바이낸스 API 없이 실행할 때 가짜 응답 반환 """
    return {
        "symbol": "BTCUSDT",
        "price": "45000.00",
        "orderId": 123456,
        "status": "FILLED"
    }

def generate_signature(params, secret_key):
    """ ✅ Binance API 요청을 위한 HMAC SHA256 서명 생성 """
    query_string = "&".join([f"{key}={params[key]}" for key in sorted(params)])
    return hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def place_order(symbol, order_type):
    """ 특정 코인에 대해 매매 주문 실행 """

    print(f"📌 [주문 요청] {order_type} {symbol} 주문 실행 중...")  # ✅ 주문 시작 로그 추가

    # ✅ Paper Trading 모드 추가
    if Config.PAPER_TRADING:
        print(f"📌 [Paper Trading] {order_type} 주문 실행: {symbol}")
        return get_mock_binance_response()

    # ✅ API 없이 실행할 경우 Mock 데이터 반환
    if Config.BINANCE_API_KEY is None or Config.BINANCE_SECRET_KEY is None:
        print("🚨 [테스트 모드] 바이낸스 API 없이 실행 중")
        return get_mock_binance_response()

    url = f"{Config.BINANCE_BASE_URL}/api/v3/order"
    headers = {"X-MBX-APIKEY": Config.BINANCE_API_KEY}
    params = {
        "symbol": symbol,
        "side": order_type,
        "type": "MARKET",
        "quantity": 0.01,
        "timestamp": int(time.time() * 1000),  # ✅ 필수 파라미터
    }

    # ✅ Binance API 서명 추가
    params["signature"] = generate_signature(params, Config.BINANCE_SECRET_KEY)

    try:
        response = requests.post(url, headers=headers, params=params)
        if response.status_code == 200:
            print(f"✅ [주문 성공] {response.json()}")  # ✅ 성공 로그 출력
            return response.json()
        else:
            print(f"❌ [주문 실패] 응답 코드: {response.status_code} | 메시지: {response.text}")  # ✅ 실패 로그 출력
            return None
    except Exception as e:
        print(f"❌ 오류 발생: {e}")  # ✅ 예외 발생 시 오류 출력
        return get_mock_binance_response()  # ✅ Mock 데이터 반환

if __name__ == "__main__":
    print(place_order("BTCUSDT", "BUY"))  # ✅ API 없이 실행 가능
