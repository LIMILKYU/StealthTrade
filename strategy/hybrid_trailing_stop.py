import numpy as np

def dynamic_trailing_stop(entry_price, current_price, atr, market_regime):
    """
    시장 상황에 맞는 하이브리드 트레일링 스탑 계산
    entry_price: 진입 가격
    current_price: 현재 가격
    atr: 평균 진폭 (ATR, 변동성 지표)
    market_regime: 시장 상태 ('강한 상승장', '약한 상승장', '횡보장', '약한 하락장', '강한 하락장')
    """
    
    if market_regime == "강한 상승장":
        trailing_stop = entry_price + atr * 4  # 강한 상승 시, 추세 길게 유지
    elif market_regime == "약한 상승장":
        trailing_stop = entry_price + atr * 3  # 보수적인 추세 유지
    elif market_regime == "강한 하락장":
        trailing_stop = entry_price - atr * 4  # 숏 포지션 추세 길게 유지
    elif market_regime == "약한 하락장":
        trailing_stop = entry_price - atr * 3  # 보수적인 하락 추세 유지
    else:  # 횡보장
        trailing_stop = entry_price - atr * 2  # 짧은 변동성을 고려한 최소 리스크 조정
    
    return max(trailing_stop, current_price - atr * 2) if current_price > entry_price else min(trailing_stop, current_price + atr * 2)

def calculate_take_profit(entry_price, atr, market_regime):
    """
    시장 상황에 맞는 동적 익절(Take-Profit) 계산
    entry_price: 진입 가격
    atr: 평균 진폭 (ATR, 변동성 지표)
    market_regime: 시장 상태 ('강한 상승장', '약한 상승장', '횡보장', '약한 하락장', '강한 하락장')
    """
    
    if market_regime == "강한 상승장":
        take_profit = entry_price + atr * 6  # 상승 추세 최대 활용
    elif market_regime == "약한 상승장":
        take_profit = entry_price + atr * 5  # 적절한 익절 목표 설정
    elif market_regime == "강한 하락장":
        take_profit = entry_price - atr * 6  # 숏 포지션에서 큰 수익 가능
    elif market_regime == "약한 하락장":
        take_profit = entry_price - atr * 5  # 보수적인 하락 추세 수익 확보
    else:  # 횡보장
        take_profit = entry_price + atr * 3  # 짧은 익절 설정하여 변동성 대응
    
    return take_profit
