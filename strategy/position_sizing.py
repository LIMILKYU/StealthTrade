import numpy as np

def kelly_criterion(win_rate, risk_reward_ratio):
    """
    켈리 기준 (Kelly Criterion) 기반 최적 포지션 크기 계산
    win_rate: 승률 (0 ~ 1 범위)
    risk_reward_ratio: 손익비 (예: 2.0이면 1:2 손익비)
    """
    kelly_fraction = win_rate - ((1 - win_rate) / risk_reward_ratio)
    return max(0, kelly_fraction)  # 음수일 경우 0으로 설정 (베팅 금지)

def calculate_volatility_adjusted_size(account_balance, atr, base_risk=0.01):
    """
    변동성(ATR) 기반 포지션 크기 조정
    account_balance: 현재 계좌 잔고
    atr: 평균 진폭 (ATR)
    base_risk: 기본 리스크 (예: 1% = 0.01)
    """
    risk_amount = account_balance * base_risk
    position_size = risk_amount / atr  # 변동성이 클수록 포지션 크기 축소
    return position_size

def determine_position_size(account_balance, market_regime, win_rate, risk_reward_ratio, atr):
    """
    시장 상황 & 켈리 기준 기반 포지션 크기 결정
    """
    kelly_size = kelly_criterion(win_rate, risk_reward_ratio)
    volatility_adjusted_size = calculate_volatility_adjusted_size(account_balance, atr)
    
    if market_regime == "강한 상승장":
        return volatility_adjusted_size * kelly_size * 1.5  # 적극적 포지션 증가
    elif market_regime == "약한 상승장":
        return volatility_adjusted_size * kelly_size * 1.2
    elif market_regime == "강한 하락장":
        return volatility_adjusted_size * kelly_size * 1.5 * -1  # 숏 포지션 증가
    elif market_regime == "약한 하락장":
        return volatility_adjusted_size * kelly_size * 1.2 * -1
    else:  # 횡보장
        return volatility_adjusted_size * kelly_size * 0.5  # 리스크 축소
