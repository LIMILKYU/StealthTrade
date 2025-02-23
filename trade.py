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
from select_coins import CoinSelector  # ✅ 자동 코인 변경 기능 추가

# ✅ 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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

def get_balance():
    """ ✅ 계좌 잔고 조회 함수 (Config에 추가 필요) """
    try:
        response = requests.get(f"{Config.BINANCE_BASE_URL}/api/v3/account", headers={
            "X-MBX-APIKEY": Config.BINANCE_API_KEY
        })
        response.raise_for_status()
        return response.json()["balances"]
    except requests.RequestException as e:
        logger.error(f"🚨 계좌 잔고 조회 실패: {e}")
        return None

def trade(symbol, order_type, win_rate, risk_reward_ratio, stop_loss_percent, volatility, volume):
    """ ✅ 변동성 & 거래량 기반으로 최적화된 주문 실행 """
    logger.info(f"📌 [주문 요청] {order_type.upper()} {symbol} 주문 실행 중...")  

    # ✅ 현재 계좌 잔고 가져오기
    balance = get_balance()
    if balance is None:
        logger.error("🚨 [API 오류] 계좌 잔고 조회 실패 → 주문 취소")
        return None

    # ✅ 레버리지 자동 조절
    leverage = leverage_manager.set_leverage(symbol)

    # ✅ AI 변동성 분석 (실시간 조정)
    ai_volatility_factor = ai_optimizer.get_volatility_factor(symbol)

    # ✅ 시장 미세구조 분석 (HFT 패턴, Iceberg 주문 감지, Order Flow Imbalance)
    market_signal = microstructure_analyzer.analyze_market()
    logger.info(f"📊 [시장 분석] {market_signal}")

    # ✅ 손절 위치 최적화 (ATR + 볼린저 밴드 + AI 스탑헌팅 감지)
    optimized_stop_loss = stop_loss_optimizer.calculate_stop_loss(symbol, stop_loss_percent, market_signal)
    logger.info(f"🔍 [손절 최적화] 최적 손절값: {optimized_stop_loss:.2f}%")

    # ✅ 최적화된 주문 크기 계산
    position_size = position_sizer.calculate_position_size(balance, symbol, win_rate, risk_reward_ratio, volatility, volume)
    logger.info(f"📌 [포지션 크기] {position_size:.4f} {symbol}")

    # ✅ 최종 주문 실행
    try:
        params = {
            "symbol": symbol,
            "side": order_type.upper(),
            "type": "MARKET",
            "quantity": position_size,
            "timestamp": int(time.time() * 1000)
        }
        params["signature"] = generate_signature(params, Config.BINANCE_SECRET_KEY)

        headers = {"X-MBX-APIKEY": Config.BINANCE_API_KEY}
        response = requests.post(f"{Config.BINANCE_BASE_URL}/api/v3/order", headers=headers, params=params)
        response.raise_for_status()
        order_result = response.json()
        logger.info(f"✅ [주문 성공] {order_result}")
        return order_result
    except requests.RequestException as e:
        logger.error(f"🚨 [주문 실패] {e}")
        return None
