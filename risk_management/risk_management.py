import logging

class RiskManagement:
    def __init__(self, balance_threshold: float, max_loss_streak: int = 3):
        """
        :param balance_threshold: 최소 유지해야 할 계좌 잔고
        :param max_loss_streak: 연속 손실 허용 횟수
        """
        self.balance_threshold = balance_threshold
        self.loss_streak = 0
        self.max_loss_streak = max_loss_streak
        self.market_condition = "Range"  # 기본값: 박스권
        logging.basicConfig(level=logging.INFO)

    def set_market_condition(self, condition: str):
        """ 시장 상태 업데이트 """
        valid_conditions = ["Strong Bullish", "Weak Bullish", "Range", "Weak Bearish", "Strong Bearish"]
        if condition not in valid_conditions:
            raise ValueError(f"Invalid market condition: {condition}")
        self.market_condition = condition
        logging.info(f"Market Condition Updated: {self.market_condition}")

    def get_dynamic_stop_loss(self):
        """ 시장 상황에 따라 손절 범위 조정 """
        stop_loss_settings = {
            "Strong Bullish": 0.05,  # 상승장 → 손절 5% (넓게 설정)
            "Weak Bullish": 0.03,  # 약한 상승장 → 손절 3%
            "Range": 0.02,  # 박스권 → 손절 2%
            "Weak Bearish": 0.01,  # 약한 하락장 → 손절 1%
            "Strong Bearish": 0.005  # 강한 하락장 → 손절 0.5% (짧게 설정)
        }
        return stop_loss_settings[self.market_condition]

    def check_balance(self, current_balance: float):
        """ 계좌 잔고 확인하여 리스크 감지 """
        if current_balance < self.balance_threshold:
            logging.warning("🚨 계좌 잔고가 안전 수준 이하! 트레이딩 중지를 고려해야 합니다. 🚨")
            return False
        return True

    def update_loss_streak(self, is_loss: bool):
        """ 연속 손실 감지 및 트레이딩 중단 조건 체크 """
        if is_loss:
            self.loss_streak += 1
        else:
            self.loss_streak = 0  # 이익 발생 시 초기화

        if self.loss_streak >= self.max_loss_streak:
            logging.warning("🚨 연속 손실 초과! 자동으로 트레이딩을 중지합니다. 🚨")
            return False
        return True

# 사용 예시
if __name__ == "__main__":
    risk_manager = RiskManagement(5000)
    risk_manager.set_market_condition("Strong Bearish")  # 강한 하락장 설정
    stop_loss = risk_manager.get_dynamic_stop_loss()
    print(f"Recommended Stop-Loss: {stop_loss*100:.2f}%")
    print(risk_manager.check_balance(4500))  # False (계좌 보호 필요)
    print(risk_manager.update_loss_streak(True))  # 연속 손실 감지

# 시장 상황에 따른 손실 제한 최적화 추가 완료!
# 강한 상승장에서는 손절 폭을 넓게
# 강한 하락장에서는 손절을 짧게 조정하여 빠르게 대응
# 연속 손실 감지 시 자동으로 트레이딩 중단 가능