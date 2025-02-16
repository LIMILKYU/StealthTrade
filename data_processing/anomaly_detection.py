# 📌 고급 이상 탐지 기법
# ✅ 통계 기반 이상 탐지 → IQR, Z-Score, MAD(중위 절대 편차)
# ✅ 머신러닝 기반 이상 탐지 → Isolation Forest, DBSCAN
# ✅ 스푸핑 감지 → 대량 주문(호가창 분석), 취소율 분석
# ✅ 비정상적인 가격 변동 감지 → 급격한 변동성, 체결 비율 분석
# ✅ 거래량 이상치 감지 → 정상적인 거래 패턴 벗어남

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from scipy.stats import zscore, iqr

class AnomalyDetection:
    def __init__(self, df):
        """
        이상 탐지 및 스푸핑 감지 클래스
        :param df: OHLCV 및 주문 데이터 (Pandas DataFrame)
        """
        self.df = df.copy()

    def z_score_outliers(self, threshold=3):
        """
        Z-Score 기반 이상 탐지
        :param threshold: Z-Score 임계값 (기본값=3)
        """
        self.df["zscore"] = np.abs(zscore(self.df["close"]))
        self.df["zscore_outlier"] = self.df["zscore"] > threshold

    def iqr_outliers(self):
        """
        IQR (Interquartile Range) 기반 이상 탐지
        """
        q1 = self.df["close"].quantile(0.25)
        q3 = self.df["close"].quantile(0.75)
        iqr_value = iqr(self.df["close"])
        lower_bound = q1 - (1.5 * iqr_value)
        upper_bound = q3 + (1.5 * iqr_value)
        self.df["iqr_outlier"] = (self.df["close"] < lower_bound) | (self.df["close"] > upper_bound)

    def isolation_forest(self, contamination=0.01):
        """
        Isolation Forest 기반 이상 탐지
        :param contamination: 이상 데이터 비율
        """
        scaler = StandardScaler()
        features = ["close", "volume", "high", "low"]
        X = scaler.fit_transform(self.df[features])
        model = IsolationForest(contamination=contamination, random_state=42)
        self.df["isolation_forest_outlier"] = model.fit_predict(X) == -1

    def dbscan_outliers(self, eps=0.5, min_samples=5):
        """
        DBSCAN 기반 이상 탐지
        :param eps: 거리 임계값
        :param min_samples: 최소 샘플 개수
        """
        scaler = StandardScaler()
        features = ["close", "volume"]
        X = scaler.fit_transform(self.df[features])
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X)
        self.df["dbscan_outlier"] = labels == -1

    def detect_spoofing(self, cancel_threshold=0.8):
        """
        스푸핑(대량 주문 후 취소) 탐지
        :param cancel_threshold: 취소율 임계값 (0.8 = 80% 이상 취소 시 스푸핑 의심)
        """
        self.df["cancel_rate"] = self.df["canceled_orders"] / (self.df["placed_orders"] + 1e-5)
        self.df["spoofing_detected"] = self.df["cancel_rate"] > cancel_threshold

    def detect_abnormal_volatility(self, threshold=2):
        """
        비정상적인 변동성 감지 (가격 급변 구간)
        :param threshold: 표준편차 기준 변동성 임계값
        """
        self.df["price_change"] = self.df["close"].pct_change()
        mean_change = self.df["price_change"].mean()
        std_change = self.df["price_change"].std()
        self.df["abnormal_volatility"] = np.abs(self.df["price_change"] - mean_change) > (threshold * std_change)

    def detect_abnormal_volume(self, threshold=3):
        """
        비정상적인 거래량 탐지 (평균 대비 이상거래 감지)
        :param threshold: 표준편차 기준 거래량 이상치 탐지 임계값
        """
        self.df["volume_zscore"] = np.abs(zscore(self.df["volume"]))
        self.df["abnormal_volume"] = self.df["volume_zscore"] > threshold

    def process_all(self):
        """
        모든 이상 탐지 실행
        """
        self.z_score_outliers()
        self.iqr_outliers()
        self.isolation_forest()
        self.dbscan_outliers()
        self.detect_spoofing()
        self.detect_abnormal_volatility()
        self.detect_abnormal_volume()

# 사용 예시
# df = pd.read_csv("market_data.csv")
# ad = AnomalyDetection(df)
# ad.process_all()
# print(ad.df.head())
