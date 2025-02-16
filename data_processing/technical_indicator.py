# 📌 주요 분석 항목
# ✅ 가격 기반 지표 → 이동평균선(SMA, EMA), VWAP, ATR
# ✅ 모멘텀 기반 지표 → RSI, Stochastic, ADX
# ✅ 거래량 기반 지표 → OBV, MFI, Chaikin Money Flow
# ✅ 복합 지표 → MACD, CCI, Bollinger Bands

import numpy as np
import pandas as pd
import talib

class TechnicalIndicators:
    def __init__(self, df):
        """
        기술적 분석 지표 계산 클래스
        :param df: OHLCV 데이터
        """
        self.df = df

    def calculate_sma(self, period=20):
        """
        단순 이동평균선 (SMA) 계산
        """
        self.df[f'SMA_{period}'] = self.df['close'].rolling(window=period).mean()
    
    def calculate_ema(self, period=20):
        """
        지수 이동평균선 (EMA) 계산
        """
        self.df[f'EMA_{period}'] = talib.EMA(self.df['close'], timeperiod=period)

    def calculate_vwap(self):
        """
        거래량 가중 평균 가격 (VWAP) 계산
        """
        self.df['VWAP'] = (self.df['close'] * self.df['volume']).cumsum() / self.df['volume'].cumsum()

    def calculate_atr(self, period=14):
        """
        평균 진폭 범위 (ATR) 계산
        """
        self.df['ATR'] = talib.ATR(self.df['high'], self.df['low'], self.df['close'], timeperiod=period)

    def calculate_rsi(self, period=14):
        """
        상대 강도 지수 (RSI) 계산
        """
        self.df['RSI'] = talib.RSI(self.df['close'], timeperiod=period)

    def calculate_macd(self):
        """
        이동평균 수렴·확산지수 (MACD) 계산
        """
        self.df['MACD'], self.df['MACD_Signal'], self.df['MACD_Hist'] = talib.MACD(
            self.df['close'], fastperiod=12, slowperiod=26, signalperiod=9
        )

    def calculate_bollinger_bands(self, period=20):
        """
        볼린저 밴드 계산
        """
        self.df['Upper_BB'], self.df['Middle_BB'], self.df['Lower_BB'] = talib.BBANDS(
            self.df['close'], timeperiod=period, nbdevup=2, nbdevdn=2, matype=0
        )

    def calculate_obv(self):
        """
        거래량 기반 지표 - OBV (On-Balance Volume)
        """
        self.df['OBV'] = talib.OBV(self.df['close'], self.df['volume'])

    def calculate_adx(self, period=14):
        """
        평균 방향성 지수 (ADX) 계산
        """
        self.df['ADX'] = talib.ADX(self.df['high'], self.df['low'], self.df['close'], timeperiod=period)

    def calculate_cci(self, period=20):
        """
        상품 채널 지수 (CCI) 계산
        """
        self.df['CCI'] = talib.CCI(self.df['high'], self.df['low'], self.df['close'], timeperiod=period)

    def calculate_cmf(self, period=20):
        """
        Chaikin Money Flow (CMF) 계산
        """
        mfv = ((self.df['close'] - self.df['low']) - (self.df['high'] - self.df['close'])) / (self.df['high'] - self.df['low']) * self.df['volume']
        self.df['CMF'] = mfv.rolling(window=period).sum() / self.df['volume'].rolling(window=period).sum()

    def calculate_all_indicators(self):
        """
        모든 지표를 한 번에 계산
        """
        self.calculate_sma()
        self.calculate_ema()
        self.calculate_vwap()
        self.calculate_atr()
        self.calculate_rsi()
        self.calculate_macd()
        self.calculate_bollinger_bands()
        self.calculate_obv()
        self.calculate_adx()
        self.calculate_cci()
        self.calculate_cmf()

# 사용 예시
# df = pd.read_csv("ohlcv_data.csv")
# indicators = TechnicalIndicators(df)
# indicators.calculate_all_indicators()
# print(df.tail())
