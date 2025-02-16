import logging
import numpy as np

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

    def calculate_position_size(self, win_rate: float, risk_reward_ratio: float, stop_loss_percent: float, volatility: float, trade_type: str):
        """
        시장 상황 & 변동성 고려하여 최적 포지션 크기 계산
        :param win_rate: 승률 (0.6 = 60%)
        :param risk_reward_ratio: 손익비 (예: 2.0 = 1:2)
        :param stop_loss_percent: 손절 비율 (예: 1% = 0.01)
        :param volatility: 최근 변동성 (예: 1.5%)
        :param trade_type: "LONG" 또는 "SHORT"
        :return: 추천 진입 금액 (USDT)
        """
        if self.market_condition == "Strong Bearish" and trade_type == "LONG":
            logging.warning("🚨 강한 하락장에서는 롱 포지션 진입 금지! 🚨")
            return 0  # 강한 하락장에서 롱 포지션 X
        
        kelly_fraction = self.kelly_criterion(win_rate, risk_reward_ratio)
        risk_amount = self.balance * self.risk_tolerance * kelly_fraction  # 켈리 적용된 리스크 금액

        # 📌 시장 상황에 따른 포지션 크기 조절
        market_adjustment = {
            "Strong Bullish": 1.0,  # 강한 상승장 → 100% 반영
            "Weak Bullish": 0.7,  # 약한 상승장 → 70% 반영
            "Range": 0.5,  # 박스권 → 50% 반영
            "Weak Bearish": 0.3,  # 약한 하락장 → 30% 반영
            "Strong Bearish": 0.5 if trade_type == "SHORT" else 0.0  # 강한 하락장 → 숏은 허용, 롱은 금지
        }
        adjusted_size = risk_amount / (stop_loss_percent * volatility) * market_adjustment[self.market_condition]

        logging.info(f"Market Condition: {self.market_condition}, Trade Type: {trade_type}, Position Size: {adjusted_size:.4f} USDT")
        return min(adjusted_size, self.balance * 0.3)  # 포지션 크기 최대 30% 제한

# 사용 예시
if __name__ == "__main__":
    position_sizing = PositionSizing(10000)  # 초기 자본금 10,000 USDT
    position_sizing.set_market_condition("Strong Bearish")  # 강한 하락장 설정
    size_long = position_sizing.calculate_position_size(0.6, 2.0, 0.01, 1.5, "LONG")
    size_short = position_sizing.calculate_position_size(0.6, 2.0, 0.01, 1.5, "SHORT")
    print(f"Recommended Long Position Size: {size_long:.2f} USDT")
    print(f"Recommended Short Position Size: {size_short:.2f} USDT")
