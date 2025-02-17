# 트레이딩 결과를 평가하고 수익률(ROI), 승률, MDD(최대 손실), 샤프비율을 계산
#AI 모델이 실전 트레이딩 결과를 분석하여 전략을 조정할 수 있도록 데이터 제공

import pandas as pd
import numpy as np
from telegram_alert import send_telegram_message

# 트레이딩 데이터 불러오기 (예제 CSV 파일)
TRADING_DATA_PATH = "trading_history.csv"

def analyze_performance():
    """ 여러 코인의 트레이딩 성과 분석 """
    try:
        df = pd.read_csv(TRADING_DATA_PATH)
        selected_coins = get_selected_coins()
        report = "📊 **트레이딩 성과 보고서**\n"

        for coin in selected_coins:
            coin_df = df[df["symbol"] == coin]

            if coin_df.empty:
                report += f"⚠️ {coin} 데이터 없음\n"
                continue

            win_rate = coin_df[coin_df["profit"] > 0].shape[0] / coin_df.shape[0]
            roi = (coin_df["profit"].sum() / coin_df["investment"].sum()) * 100
            max_drawdown = ((coin_df["cumulative_profit"].cummax() - coin_df["cumulative_profit"]) / coin_df["cumulative_profit"].cummax()).min() * 100

def analyze_performance():
    """ 트레이딩 성과 분석 (ROI, 승률, MDD 계산) """
    try:
        df = pd.read_csv(TRADING_DATA_PATH)

        # ✅ 승률 계산 (총 이익 거래 / 전체 거래 수)
        win_rate = df[df["profit"] > 0].shape[0] / df.shape[0]

        # ✅ ROI (Return on Investment) 계산
        total_profit = df["profit"].sum()
        total_investment = df["investment"].sum()
        roi = (total_profit / total_investment) * 100

        # ✅ MDD (Maximum Drawdown) 계산
        df["cumulative_profit"] = df["profit"].cumsum()
        rolling_max = df["cumulative_profit"].cummax()
        drawdown = (df["cumulative_profit"] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100  # 백분율 변환

        # ✅ 리포트 출력
        report = f"""
        📊 **트레이딩 성과 보고서**
        ✅ 승률: {win_rate * 100:.2f}%
        ✅ ROI: {roi:.2f}%
        ✅ 최대 손실 (MDD): {max_drawdown:.2f}%
        ✅ 총 거래 횟수: {df.shape[0]} 회
        ✅ 총 수익: {total_profit:.2f} USDT
        """

        return report.strip()

    except Exception as e:
        return f"❌ 성과 분석 오류: {str(e)}"

def send_trading_report():
    """ 트레이딩 성과 분석 후 텔레그램으로 보고서 전송 """
    report = analyze_performance()
    send_telegram_message(report)

# 실행 코드
if __name__ == "__main__":
    send_trading_report()


