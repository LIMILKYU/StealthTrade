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
from strategy.leverage_manager import LeverageManager  
from strategy.market_microstructure import MarketMicrostructureAnalyzer  
from strategy.stop_loss_optimizer import StopLossOptimizer  
from select_coins import CoinSelector  # ✅ 신규 추가 (자동 코인 변경)

# ✅ 포지션 크기 조정 및 최적화 객체 생성
position_sizer = PositionSizing()
ai_optimizer = AIRealTimeOptimizer()
leverage_manager = LeverageManager()  
microstructure_analyzer = MarketMicrostructureAnalyzer("btcusdt")  # ✅ WebSocket 연동
stop_loss_optimizer = StopLossOptimizer()
coin_selector = CoinSelector()  # ✅ 자동 코인 변경 기능 추가

def generate_signature(params, secret_key):
    """ ✅ Binance API 요청을 위한 HMAC SHA256 서명 생성 """
    query_string = "&".join([f"{key}={params[key]}" for key in sorted(params)])
    return hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def trade(symbol, order_type, win_rate, risk_reward_ratio, stop_loss_percent, volatility, volume):
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

    # ✅ 시장 미세구조 분석 (HFT 패턴, Iceberg 주문 감지, Order Flow Imbalance)
    market_signal = microstructure_analyzer.analyze_market()
    print(f"📊 [시장 분석] {market_signal}")

    # ✅ 손절 위치 최적화 (ATR + 볼린저 밴드 + AI 스탑헌팅 감지)
    optimized_stop_loss = stop_loss_optimizer.calculate_stop_loss(symbol, stop_loss_percent, market_signal)
    print(f"🔍 [손절 최적화] 최적 손절값: {optimized_stop_loss:.2f}%")

    # ✅ 최적화된 주문 크기 계산
    position_size = position_sizer.calculate_position_size(
        win_rate=win_rate, 
        risk_reward_ratio=risk_reward_ratio, 
        stop_loss_percent=optimized_stop_loss,  
        volatility=volatility, 
        volume=volume, 
        trade_type=order_type, 
        ai_volatility_factor=ai_volatility_factor
    )

    if position_size <= 0:
        print(f"🚨 [주문 취소] {symbol} 주문이 위험 요소로 인해 실행되지 않음.")
        return None

    # ✅ Binance API 주문 실행
    url = f"{Config.BINANCE_BASE_URL}/api/v3/order"
    headers = {"X-MBX-APIKEY": Config.BINANCE_API_KEY}
    params = {
        "symbol": symbol,
        "side": order_type,
        "type": "MARKET",
        "quoteOrderQty": position_size,  
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

def run_trading_cycle():
    """ ✅ 자동매매 주기 실행 (매매 후 종목 변경 판단) """
    current_coin = "BTCUSDT"
    while True:
        print(f"🚀 [자동매매 시작] 현재 거래 코인: {current_coin}")

        trade_result = trade(
            current_coin, 
            "BUY", 
            win_rate=60, 
            risk_reward_ratio=2.0, 
            stop_loss_percent=1.5, 
            volatility=0.02, 
            volume=500
        )

        time.sleep(10)  # 매매 후 대기

        # ✅ 매매 완료 후 새로운 코인으로 변경할지 판단
        current_coin = coin_selector.should_switch_coin(current_coin)

if __name__ == "__main__":
    run_trading_cycle()
