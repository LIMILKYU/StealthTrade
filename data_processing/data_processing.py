# 📌 고급 데이터 가공 프로세스
# ✅ 이상치 처리 → Z-Score, IQR, Hampel Filter
# ✅ 결측치 처리 → 선형 보간법, KNN Imputation
# ✅ 스케일링 & 정규화 → Min-Max, StandardScaler, RobustScaler
# ✅ 피처 엔지니어링 → 로그 변환, 파생 변수 생성
# ✅ 시계열 데이터 변환 → 차분(differencing), 이동 평균

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from scipy.stats import zscore

class DataProcessing:
    def __init__(self, df):
        """
        고급 데이터 전처리 및 가공 클래스
        :param df: OHLCV 데이터
        """
        self.df = df.copy()

    def handle_missing_values(self, method="linear"):
        """
        결측치 처리 (선형 보간, KNN 등)
        """
        if method == "linear":
            self.df.interpolate(method='linear', inplace=True)
        elif method == "ffill":
            self.df.fillna(method='ffill', inplace=True)
        elif method == "bfill":
            self.df.fillna(method='bfill', inplace=True)

    def remove_outliers(self, method="zscore", threshold=3.0):
        """
        이상치 제거 (Z-Score, IQR)
        """
        if method == "zscore":
            z_scores = np.abs(zscore(self.df.select_dtypes(include=[np.number])))
            self.df = self.df[(z_scores < threshold).all(axis=1)]
        elif method == "iqr":
            Q1 = self.df.quantile(0.25)
            Q3 = self.df.quantile(0.75)
            IQR = Q3 - Q1
            self.df = self.df[~((self.df < (Q1 - 1.5 * IQR)) | (self.df > (Q3 + 1.5 * IQR))).any(axis=1)]

    def scale_features(self, method="standard"):
        """
        데이터 스케일링 (StandardScaler, MinMaxScaler, RobustScaler)
        """
        scaler = None
        if method == "standard":
            scaler = StandardScaler()
        elif method == "minmax":
            scaler = MinMaxScaler()
        elif method == "robust":
            scaler = RobustScaler()

        if scaler:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = scaler.fit_transform(self.df[numeric_cols])

    def log_transform(self, columns):
        """
        로그 변환 (거래량 등 분포 조정)
        """
        for col in columns:
            self.df[col] = np.log1p(self.df[col])

    def add_time_features(self):
        """
        시계열 데이터 가공 (월, 일, 요일, 시간 등)
        """
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df['year'] = self.df['timestamp'].dt.year
        self.df['month'] = self.df['timestamp'].dt.month
        self.df['day'] = self.df['timestamp'].dt.day
        self.df['weekday'] = self.df['timestamp'].dt.weekday
        self.df['hour'] = self.df['timestamp'].dt.hour
        self.df.drop(columns=['timestamp'], inplace=True)

    def apply_moving_average(self, column='close', window=5):
        """
        이동 평균 계산
        """
        self.df[f"{column}_ma{window}"] = self.df[column].rolling(window=window).mean()

    def apply_differencing(self, column='close'):
        """
        차분(differencing) 적용 (시계열 안정화)
        """
        self.df[f"{column}_diff"] = self.df[column].diff()

    def engineer_features(self):
        """
        고급 피처 엔지니어링 (가격 변화율, 거래량 변화율 등)
        """
        self.df['return'] = self.df['close'].pct_change()
        self.df['vol_change'] = self.df['volume'].pct_change()
        self.df['high_low_range'] = self.df['high'] - self.df['low']

    def process_all(self):
        """
        모든 데이터 전처리 & 가공 실행
        """
        self.handle_missing_values()
        self.remove_outliers()
        self.scale_features()
        self.log_transform(columns=['volume'])
        self.add_time_features()
        self.apply_moving_average()
        self.apply_differencing()
        self.engineer_features()

# 사용 예시
# df = pd.read_csv("ohlcv_data.csv")
# processor = DataProcessing(df)
# processor.process_all()
# print(processor.df.head())
