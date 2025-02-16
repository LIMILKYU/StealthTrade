import numpy as np
import pandas as pd
from scipy import stats

class DataPreprocessor:
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def handle_missing_values(self, method='mean'):
        """
        결측치 처리 (평균 대체, 선형 보간, 이동 평균 적용)
        """
        if method == 'mean':
            self.data.fillna(self.data.mean(), inplace=True)
        elif method == 'median':
            self.data.fillna(self.data.median(), inplace=True)
        elif method == 'interpolate':
            self.data.interpolate(method='linear', inplace=True)
        return self.data
    
    def remove_outliers(self, method='zscore', threshold=3):
        """
        이상치 제거 (Z-score 또는 IQR 기준)
        """
        if method == 'zscore':
            z_scores = np.abs(stats.zscore(self.data.select_dtypes(include=[np.number])))
            self.data = self.data[(z_scores < threshold).all(axis=1)]
        elif method == 'iqr':
            Q1 = self.data.quantile(0.25)
            Q3 = self.data.quantile(0.75)
            IQR = Q3 - Q1
            self.data = self.data[~((self.data < (Q1 - 1.5 * IQR)) | (self.data > (Q3 + 1.5 * IQR))).any(axis=1)]
        return self.data
    
    def normalize_data(self, method='minmax'):
        """
        데이터 정규화 (Min-Max, Z-score, 로그 변환)
        """
        if method == 'minmax':
            self.data = (self.data - self.data.min()) / (self.data.max() - self.data.min())
        elif method == 'zscore':
            self.data = (self.data - self.data.mean()) / self.data.std()
        elif method == 'log':
            self.data = np.log1p(self.data)
        return self.data
    
    def add_moving_averages(self, windows=[5, 10, 20]):
        """
        이동평균 추가 (EMA 포함)
        """
        for window in windows:
            self.data[f'SMA_{window}'] = self.data['close'].rolling(window=window).mean()
            self.data[f'EMA_{window}'] = self.data['close'].ewm(span=window, adjust=False).mean()
        return self.data
    
    def calculate_volatility(self, window=14):
        """
        변동성(ATR) 계산
        """
        self.data['High-Low'] = self.data['high'] - self.data['low']
        self.data['High-Close'] = abs(self.data['high'] - self.data['close'].shift(1))
        self.data['Low-Close'] = abs(self.data['low'] - self.data['close'].shift(1))
        self.data['TrueRange'] = self.data[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)
        self.data[f'ATR_{window}'] = self.data['TrueRange'].rolling(window=window).mean()
        return self.data
    
    def process(self):
        """
        전체 전처리 과정 실행
        """
        self.handle_missing_values(method='interpolate')
        self.remove_outliers(method='iqr')
        self.normalize_data(method='zscore')
        self.add_moving_averages()
        self.calculate_volatility()
        return self.data
