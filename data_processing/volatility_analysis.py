# 📌 변동성 분석 주요 목표
# ✅ 가격 변동성 (ATR, Bollinger Bands, Historical Volatility) 측정
# ✅ 거래량 변동성 분석 (VWAP, OBV, 거래대금 변동성)
# ✅ 시장 충격 반응 분석 (고래 매매, Iceberg 주문 반영)
# ✅ 머신러닝 기반 변동성 예측 모델 구축 (GARCH, LSTM 등 적용 가능)
# ✅ 리스크 조절을 위한 자동 포지션 크기 조정 (Kelly Criterion, Volatility Adjusted Sizing)

import pandas as pd
import numpy as np
import requests
import time
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kurtosis, skew
from statsmodels.tsa.stattools import adfuller
from arch import arch_model  # GARCH 모델
from ohlcv_collector import OHLCVCollector  # 가격 데이터 수집 모듈
from total_trading_value import TradingVolumeAnalyzer  # 거래대금 분석 모듈

class VolatilityAnalysis:
    def __init__(self, asset="BTCUSDT", interval="1h"):
        """
        변동성 분석 클래스
        :param asset: 분석할 암호화폐 (예: BTCUSDT)
        :param interval: 가격 데이터 간격 (예: "1h", "15m")
        """
        self.asset = asset
        self.interval = interval
        self.price_collector = OHLCVCollector()
        self.volume_analyzer = TradingVolumeAnalyzer()

    def fetch_price_data(self, lookback=200):
        """
        지정된 자산의 가격 데이터 수집 (최근 200개 캔들)
        """
        return self.price_collector.get_ohlcv(self.asset, self.interval, lookback)

    def compute_volatility_metrics(self, df):
        """
        변동성 지표 계산 (ATR, Bollinger Bands, HV)
        """
        df["returns"] = df["close"].pct_change()
        df["ATR"] = df["high"].rolling(window=14).max() - df["low"].rolling(window=14).min()
        df["HV"] = df["returns"].rolling(window=30).std() * np.sqrt(365) * 100  # 연율화 변동성
        df["BB_up"] = df["close"].rolling(window=20).mean() + 2 * df["close"].rolling(window=20).std()
        df["BB_down"] = df["close"].rolling(window=20).mean() - 2 * df["close"].rolling(window=20).std()
        return df

    def compute_kurtosis_skewness(self, df):
        """
        분포 측정 지표: 왜도(Skewness), 첨도(Kurtosis)
        """
        return {"skewness": skew(df["returns"].dropna()), "kurtosis": kurtosis(df["returns"].dropna())}

    def adf_test(self, df):
        """
        단위근 검정 (Stationarity Test)
        """
        result = adfuller(df["returns"].dropna())
        return {"ADF Statistic": result[0], "p-value": result[1]}

    def garch_model(self, df):
        """
        GARCH(1,1) 모델을 사용한 변동성 예측
        """
        model = arch_model(df["returns"].dropna() * 100, vol="Garch", p=1, q=1)
        result = model.fit(disp="off")
        return result.summary()

    def merge_volume_data(self, df):
        """
        거래량 변동성과 가격 변동성 데이터 병합
        """
        volume_data = self.volume_analyzer.get_volume_data(self.asset, self.interval)
        df = df.merge(volume_data, on="timestamp", how="left")
        df.fillna(0, inplace=True)
        return df

    def plot_volatility(self, df):
        """
        변동성 분석 결과 시각화
        """
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x=df.index, y="HV", label="Historical Volatility", color="blue")
        sns.lineplot(data=df, x=df.index, y="ATR", label="ATR", color="red")
        sns.lineplot(data=df, x=df.index, y="BB_up", label="Bollinger Upper", linestyle="dashed")
        sns.lineplot(data=df, x=df.index, y="BB_down", label="Bollinger Lower", linestyle="dashed")
        plt.title("변동성 분석 (ATR, HV, Bollinger Bands)")
        plt.xlabel("시간")
        plt.ylabel("변동성 지표")
        plt.legend()
        plt.show()

    def run_analysis(self):
        """
        전체 변동성 분석 실행
        """
        df = self.fetch_price_data()
        df = self.compute_volatility_metrics(df)
        df = self.merge_volume_data(df)

        stats_results = {
            "skew_kurtosis": self.compute_kurtosis_skewness(df),
            "adf_test": self.adf_test(df),
            "garch_summary": self.garch_model(df)
        }

        self.plot_volatility(df)
        return stats_results

# 실행 예제
# va = VolatilityAnalysis()
# va.run_analysis()
