import requests
import json
import time
import hmac
import hashlib
from config import BINANCE_API_KEY, BINANCE_SECRET_KEY, BINANCE_BASE_URL, TRADE_SYMBOL, TRADE_AMOUNT
from ai_optimization.ai_model import LSTMAIModel

# AI 모델 로드
ai_model = LSTMAIModel(input_shape=(50, 5))

def get_binance_signature(params, secret):
    """ API 서명(Signature) 생성 """
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def place_order(symbol, order_type):
    """ 특정 코인에 대해 매매 주문 실행 (오류 처리 강화) """
    url = f"{BINANCE_BASE_URL}/api/v3/order"
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    params = {
        "symbol": symbol,
        "side": order_type,
        "type": "MARKET",
        "quantity": TRADE_AMOUNT,
        "timestamp": int(time.time() * 1000),
    }
    params["signature"] = get_binance_signature(params, BINANCE_SECRET_KEY)

    max_retries = 3
    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, params=params)
        if response.status_code == 200:
            print(f"✅ 주문 성공 ({order_type} {symbol}):", response.json())
            return response.json()
        else:
            print(f"❌ 주문 실패 ({order_type} {symbol}) [{attempt+1}/{max_retries}]:", response.text)
            time.sleep(2)  # API 요청 제한 고려

    print("🚨 주문 실패, 재시도 한도 초과!")
    return None

def execute_trades():
    """ AI 신호 기반 매매 실행 """
    prediction = ai_model.predict_latest_signal()
    order_type = "BUY" if prediction > 0.5 else "SELL"
    place_order(TRADE_SYMBOL, order_type)

if __name__ == "__main__":
    execute_trades()
