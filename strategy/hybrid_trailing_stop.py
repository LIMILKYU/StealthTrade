import numpy as np
import logging
from ai_optimization.ai_real_time_optimizer import AIRealTimeOptimizer

class HybridTrailingStop:
    def __init__(self, entry_price, current_price, atr, market_regime, leverage=1.0):
        self.entry_price = entry_price
        self.current_price = current_price
        self.atr = atr
        self.market_regime = market_regime
        self.leverage = leverage
        self.ai_optimizer = AIRealTimeOptimizer()  # AI 기반 예측
        logging.basicConfig(level=logging.INFO)

    def dynamic_trailing_stop(self):
        """ 시장 상황에 맞는 하이브리드 트레일링 스탑 계산 """
        if self.market_regime == "강한 상승장":
            trailing_stop = self.entry_price + self.atr * 4  # 강한 상승 시, 추세 길게 유지
        elif self.market_regime == "약한 상승장":
            trailing_stop = self.entry_price + self.atr * 3  # 보수적인 추세 유지
        elif self.market_regime == "강한 하락장":
            trailing_stop = self.entry_price - self.atr * 4  # 숏 포지션 추세 길게 유지
        elif self.market_regime == "약한 하락장":
            trailing_stop = self.entry_price - self.atr * 3  # 보수적인 하락 추세 유지
        else:  # 횡보장
            trailing_stop = self.entry_price - self.atr * 2  # 짧은 변동성을 고려한 최소 리스크 조정

        # AI 예측 변동성 추가 조정
        ai_volatility_factor = self.ai_optimizer.get_volatility_factor()
        trailing_stop += ai_volatility_factor * self.atr

        return max(trailing_stop, self.current_price - self.atr * 2) if self.current_price > self.entry_price else min(trailing_stop, self.current_price + self.atr * 2)

    def calculate_take_profit(self):
        """ 시장 상황에 맞는 동적 익절(Take-Profit) 계산 """
        if self.market_regime == "강한 상승장":
            take_profit = self.entry_price + self.atr * 6  # 상승 추세 최대 활용
        elif self.market_regime == "약한 상승장":
            take_profit = self.entry_price + self.atr * 5  # 적절한 익절 목표 설정
        elif self.market_regime == "강한 하락장":
            take_profit = self.entry_price - self.atr * 6  # 숏 포지션에서 큰 수익 가능
        elif self.market_regime == "약한 하락장":
            take_profit = self.entry_price - self.atr * 5  # 보수적인 하락 추세 수익 확보
        else:  # 횡보장
            take_profit = self.entry_price + self.atr * 3  # 짧은 익절 설정하여 변동성 대응

        # AI 예측 기반 익절 목표 추가 조정
        ai_take_profit_factor = self.ai_optimizer.get_take_profit_factor()
        take_profit += ai_take_profit_factor * self.atr

        return take_profit

# ✅ 사용 예시
if __name__ == "__main__":
    entry_price = 50000  # 예시 진입 가격
    current_price = 51000  # 예시 현재 가격
    atr = 200  # 예시 ATR
    market_regime = "강한 상승장"  # 예시 시장 상태

    hts = HybridTrailingStop(entry_price, current_price, atr, market_regime)
    trailing_stop = hts.dynamic_trailing_stop()
    take_profit = hts.calculate_take_profit()

    print(f"🔻 트레일링 스탑: {trailing_stop:.2f} | 🎯 익절 목표: {take_profit:.2f}")
