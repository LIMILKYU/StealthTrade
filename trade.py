import requests
import json
import time
import os
import hmac
import hashlib
import logging
from config import Config
from strategy.position_sizing import PositionSizing
from ai_optimization.ai_real_time_optimizer import AIRealTimeOptimizer
from strategy.leverage_manager import LeverageManager  # ✅ 신규 추가

# ✅ 포지션 크기 조정 객체 생성
position_sizer = PositionSizing()
ai_optimizer = AIRealTimeOptimizer()
leverage_manager = LeverageManager()  # ✅ 신규 추가

def generate_signature(params, secret_key):
    """ ✅ Binance API 요청을 위한 HMAC SHA256 서명 생성 """
    query_string = "&".join([f"{key}={params[key]}" for key in sorted(params)])
    return hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def place_order(symbol, order_type, win_rate, risk_reward_ratio, stop_loss_percent, volatility, volume):
    """ ✅ 변동성 & 거래량 기반으로 최적화된 주문 실행 """

    print(f"📌 [주문 요청] {order_type} {symbol} 주문 실행 중...")  

    # ✅ 현재 계좌 잔고 가져오기
    balance = Config.get_balance()
    if balance is None:
        print("🚨 [API 오류] 계좌 잔고 조회 실패 → 주문 취소")
        return None

    # ✅ 레버리지 자동 조절
    leverage = leverage_manager.set_leverage(symbol)

    # ✅ AI 변동성 분석 (실시간 조정)
    ai_volatility_factor = ai_optimizer.get_volatility_factor(symbol)

    # ✅ 최적화된 주문 크기 계산
    position_size = position_sizer.calculate_position_size(
        win_rate=win_rate, 
        risk_reward_ratio=risk_reward_ratio, 
        stop_loss_percent=stop_loss_percent, 
        volatility=volatility, 
        volume=volume, 
        trade_type=order_type, 
        ai_volatility_factor=ai_volatility_factor
    )

    if position_size <= 0:
        print(f"🚨 [주문 취소] {symbol} 주문이 위험 요소로 인해 실행되지 않음.")
        return None

    # ✅ Paper Trading 모드 추가
    if Config.PAPER_TRADING:
        print(f"📌 [Paper Trading] {order_type} 주문 실행: {symbol} | 크기: {position_size:.2f} USDT | 레버리지: {leverage}x")
        return {"symbol": symbol, "price": "45000.00", "orderId": 123456, "status": "FILLED"}

    # ✅ 실제 Binance API 주문 실행
    url = f"{Config.BINANCE_BASE_URL}/api/v3/order"
    headers = {"X-MBX-APIKEY": Config.BINANCE_API_KEY}
    params = {
        "symbol": symbol,
        "side": order_type,
        "type": "MARKET",
        "quoteOrderQty": position_size,  # ✅ 최적화된 자본 반영
        "timestamp": int(time.time() * 1000),
    }

    # ✅ Binance API 서명 추가
    params["signature"] = generate_signature(params, Config.BINANCE_SECRET_KEY)

    try:
        response = requests.post(url, headers=headers, params=params)
        if response.status_code == 200:
            print(f"✅ [주문 성공] {response.json()}")
            return response.json()
        else:
            print(f"❌ [주문 실패] 응답 코드: {response.status_code} | 메시지: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None
