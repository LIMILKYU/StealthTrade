# 📌 고급 특성 엔지니어링 기법
# ✅ 기본 통계 특성 → 평균, 표준편차, 중앙값, 최댓값/최솟값
# ✅ 변동성 관련 특성 → ATR, 볼린저 밴드, 일중 변동성
# ✅ 가격 모멘텀 특성 → RSI, MACD, 모멘텀 지표
# ✅ 거래량 분석 특성 → OBV, 거래량 변화율, VWAP
# ✅ 시장 심리 분석 → 공포/탐욕 지수 기반 감성 분석
# ✅ 시계열 패턴 → 차분(differencing), 이동 평균, 고유 주기성

import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
from sklearn.preprocessing import MinMaxScaler

class FeatureEngineering:
    def __init__(self, df):
        """
        머신러닝 특성 엔지니어링 클래스
        :param df: OHLCV 데이터
        """
        self.df = df.copy()
    
    def add_basic_stats(self):
        """
        기본 통계 특성 추가 (평균, 중앙값, 표준편차 등)
        """
        self.df["price_mean"] = self.df["close"].rolling(window=10).mean()
        self.df["price_median"] = self.df["close"].rolling(window=10).median()
        self.df["price_std"] = self.df["close"].rolling(window=10).std()
        self.df["price_max"] = self.df["close"].rolling(window=10).max()
        self.df["price_min"] = self.df["close"].rolling(window=10).min()

    def add_volatility_features(self):
        """
        변동성 관련 특성 추가 (ATR, 볼린저 밴드)
        """
        atr = AverageTrueRange(high=self.df["high"], low=self.df["low"], close=self.df["close"])
        self.df["ATR"] = atr.average_true_range()
        
        bb = BollingerBands(close=self.df["close"], window=20, window_dev=2)
        self.df["BB_High"] = bb.bollinger_hband()
        self.df["BB_Low"] = bb.bollinger_lband()
        self.df["BB_Width"] = bb.bollinger_wband()

    def add_momentum_features(self):
        """
        모멘텀 관련 특성 추가 (RSI, MACD, 모멘텀)
        """
        self.df["RSI"] = RSIIndicator(close=self.df["close"], window=14).rsi()
        self.df["Momentum"] = self.df["close"].diff(5)

        macd = MACD(close=self.df["close"], window_slow=26, window_fast=12, window_sign=9)
        self.df["MACD"] = macd.macd()
        self.df["MACD_Signal"] = macd.macd_signal()

    def add_volume_features(self):
        """
        거래량 관련 특성 추가 (OBV, 거래량 변화율, VWAP)
        """
        self.df["volume_change"] = self.df["volume"].pct_change()
        self.df["OBV"] = OnBalanceVolumeIndicator(close=self.df["close"], volume=self.df["volume"]).on_balance_volume()
        self.df["VWAP"] = (self.df["close"] * self.df["volume"]).cumsum() / self.df["volume"].cumsum()

    def add_sentiment_features(self):
        """
        시장 심리 분석 특성 추가 (공포/탐욕 지수, 감성 분석)
        """
        self.df["fear_greed_index"] = np.random.uniform(0, 1, len(self.df))  # 실제 데이터 연동 필요

    def add_time_features(self):
        """
        시계열 패턴 분석 (요일, 시간대, 주기성)
        """
        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
        self.df["hour"] = self.df["timestamp"].dt.hour
        self.df["dayofweek"] = self.df["timestamp"].dt.dayofweek

    def scale_features(self):
        """
        특성 스케일링 (MinMaxScaler)
        """
        scaler = MinMaxScaler()
        feature_cols = ["price_mean", "price_std", "ATR", "RSI", "Momentum", "MACD", "VWAP"]
        self.df[feature_cols] = scaler.fit_transform(self.df[feature_cols])

    def process_all(self):
        """
        모든 특성 생성 실행
        """
        self.add_basic_stats()
        self.add_volatility_features()
        self.add_momentum_features()
        self.add_volume_features()
        self.add_sentiment_features()
        self.add_time_features()
        self.scale_features()

# 사용 예시
# df = pd.read_csv("ohlcv_data.csv")
# fe = FeatureEngineering(df)
# fe.process_all()
# print(fe.df.head())

