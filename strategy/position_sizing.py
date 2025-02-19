import logging
import numpy as np
from config import Config  # ✅ Binance API에서 실시간 자본금 가져오기

class PositionSizing:
    def __init__(self, initial_balance: float, risk_tolerance: float = 0.02):
        """
        :param initial_balance: 초기 자본금
        :param risk_tolerance: 기본 리스크 허용 비율 (기본: 2%)
        """
        self.balance = initial_balance
        self.risk_tolerance = risk_tolerance
        self.market_condition = "Range"  # 초기 시장 상태 (기본: 박스권)
        logging.basicConfig(level=logging.INFO)

    def set_market_condition(self, condition: str):
        """ 현재 시장 상태 업데이트 """
        valid_conditions = ["Strong Bullish", "Weak Bullish", "Range", "Weak Bearish", "Strong Bearish"]
        if condition not in valid_conditions:
            raise ValueError(f"Invalid market condition: {condition}")
        self.market_condition = condition
        logging.info(f"Market Condition Updated: {self.market_condition}")

    def get_current_balance(self):
        """ ✅ Binance API에서 현재 USDT 잔고 가져오기 """
        balance = Config.get_balance()
        if balance is None:
            logging.error("❌ [잔고 오류] Binance API에서 자본금 가져오기 실패! 기본값 100 USDT 사용.")
            return 100  # 기본값
        return balance
        
    def kelly_criterion(self, win_rate: float, risk_reward_ratio: float):
        """
        켈리 공식 적용하여 최적 포지션 크기 계산
        :param win_rate: 승률 (예: 0.6 = 60%)
        :param risk_reward_ratio: 손익비 (예: 2.0 = 1:2)
        :return: 추천 투자 비율 (최대 30% 제한)
        """
        kelly_fraction = win_rate - (1 - win_rate) / risk_reward_ratio
        optimal_fraction = max(0, min(kelly_fraction, 0.3))  # 0% ~ 30% 제한
        logging.info(f"Kelly Criterion Position Size: {optimal_fraction:.2%}")
        return optimal_fraction

    def calculate_position_size(self, win_rate: float, risk_reward_ratio: float, stop_loss_percent: float, 
                                volatility: float, volume: float, trade_type: str, ai_volatility_factor: float):
        """
        변동성 & 거래량을 반영하여 최적 포지션 크기 계산
        :param win_rate: 승률 (0.6 = 60%)
        :param risk_reward_ratio: 손익비 (예: 2.0 = 1:2)
        :param stop_loss_percent: 손절 비율 (예: 1% = 0.01)
        :param volatility: 최근 변동성 (예: 1.5%)
        :param volume: 최근 거래량 (예: 500 BTC)
        :param trade_type: "LONG" 또는 "SHORT"
        :param ai_volatility_factor: AI 기반 변동성 가중치
        :return: 추천 진입 금액 (USDT)
        """
        if self.market_condition == "Strong Bearish" and trade_type == "LONG":
            logging.warning("🚨 강한 하락장에서는 롱 포지션 진입 금지! 🚨")
            return 0

        # 켈리 공식 기반 포지션 크기 계산
        base_fraction = self.kelly_criterion(win_rate, risk_reward_ratio)

        # 변동성 & 거래량 기반 자본 배분 가중치 적용
        volatility_weight = np.clip(volatility * ai_volatility_factor, 0.5, 2.0)  # 변동성 높은 코인은 2배 증가 가능
        volume_weight = np.clip(volume / 1000, 0.5, 2.0)  # 거래량이 많으면 가중치 증가

        # 전체 포지션 크기 계산
        position_size = self.balance * base_fraction * volatility_weight * volume_weight

        # 리스크 관리 (자본금의 최대 10% 제한)
        max_position_size = self.balance * 0.10
        position_size = min(position_size, max_position_size)

        logging.info(f"Calculated Position Size: {position_size:.2f} USDT (Volatility Factor: {volatility_weight:.2f}, Volume Factor: {volume_weight:.2f})")

        return position_size
