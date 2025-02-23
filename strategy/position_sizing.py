import logging
import numpy as np
from config import Config

class PositionSizing:
    def __init__(self, initial_balance: float, risk_tolerance: float = 0.02, selected_coins: list = ["BTCUSDT"]):
        """
        :param initial_balance: 초기 자본금
        :param risk_tolerance: 기본 리스크 허용 비율 (기본: 2%)
        :param selected_coins: 다중 코인 지원 (기본: BTCUSDT)
        """
        self.balance = initial_balance
        self.risk_tolerance = risk_tolerance
        self.selected_coins = selected_coins  # 다중 코인 지원
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
        """ Binance API에서 현재 잔고 가져오기 """
        balance = Config.get_balance()
        if balance is None:
            logging.error("❌ [잔고 오류] Binance API에서 자본금 가져오기 실패! 기본값 100 USDT 사용.")
            return 100  # 기본값
        return balance

    def kelly_criterion(self, win_rate: float, risk_reward_ratio: float):
        """ 켈리 공식 적용하여 최적 포지션 크기 계산 """
        kelly_fraction = win_rate - (1 - win_rate) / risk_reward_ratio
        optimal_fraction = max(0, min(kelly_fraction, 0.3))  # 0% ~ 30% 제한
        logging.info(f"Kelly Criterion Position Size: {optimal_fraction:.2%}")
        return optimal_fraction

    def calculate_position_size(self, win_rate: float, risk_reward_ratio: float, stop_loss_percent: float, 
                                volatility: float, volume: float, trade_type: str, ai_volatility_factor: float):
        """
        변동성 & 거래량을 반영하여 포지션 크기 계산
        """
        # 켈리 기준에 따른 포지션 크기 계산
        kelly_fraction = self.kelly_criterion(win_rate, risk_reward_ratio)
        
        # 변동성 및 거래량을 고려한 포지션 크기 계산
        position_size = (self.balance * kelly_fraction) / (stop_loss_percent * volatility * ai_volatility_factor)
        
        # 시장 상태에 따른 추가 조정 (예: 상승장에서는 포지션 크기 확대)
        if self.market_condition == "Strong Bullish":
            position_size *= 1.5
        elif self.market_condition == "Strong Bearish":
            position_size *= 0.5

        position_size = min(position_size, self.balance * 0.3)  # 최대 30% 자본까지 투자

        logging.info(f"Calculated Position Size: {position_size:.2f}")
        return position_size

# ✅ 사용 예시
if __name__ == "__main__":
    ps = PositionSizing(initial_balance=10000, selected_coins=["BTCUSDT", "ETHUSDT"])

    # 예시 파라미터
    win_rate = 0.6  # 60% 승률
    risk_reward_ratio = 2.0  # 손익비 2:1
    stop_loss_percent = 0.02  # 손절 퍼센트 2%
    volatility = 0.03  # 변동성
    volume = 50000000  # 거래량 (예시)
    ai_volatility_factor = 1.5  # AI 변동성 계수 (예시)
    
    for coin in ps.selected_coins:
        position_size = ps.calculate_position_size(win_rate, risk_reward_ratio, stop_loss_percent, 
                                                   volatility, volume, "buy", ai_volatility_factor)
        print(f"포지션 크기 ({coin}): {position_size:.2f} USDT")
