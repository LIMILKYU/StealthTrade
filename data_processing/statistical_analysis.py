# ✅ 시계열 분석 → 추세, 계절성, 이상값 감지
# ✅ 상관관계 분석 → Pearson, Spearman, Kendall
# ✅ 분포 분석 → 히스토그램, KDE, 분산, 왜도, 첨도
# ✅ 변동성 분석 → 이동 평균(MA), 지수이동평균(EMA), ATR
# ✅ 시장 미세구조 분석 → 호가창 기반 유동성 및 깊이 분석

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr, kendalltau, skew, kurtosis
from statsmodels.tsa.seasonal import seasonal_decompose

class StatisticalAnalysis:
    def __init__(self, df):
        """
        통계 분석 클래스
        :param df: OHLCV 데이터 (시계열 데이터)
        """
        self.df = df
    
    def time_series_analysis(self, column='close'):
        """
        시계열 분석 - 추세, 계절성, 이상값 감지
        """
        decomposition = seasonal_decompose(self.df[column], model='additive', period=24)
        decomposition.plot()
        plt.show()
    
    def correlation_analysis(self):
        """
        상관관계 분석 (Pearson, Spearman, Kendall)
        """
        print("📌 Pearson Correlation:", pearsonr(self.df['open'], self.df['close']))
        print("📌 Spearman Correlation:", spearmanr(self.df['open'], self.df['close']))
        print("📌 Kendall Correlation:", kendalltau(self.df['open'], self.df['close']))
    
    def distribution_analysis(self, column='close'):
        """
        데이터 분포 분석 (히스토그램, KDE, 분산, 왜도, 첨도)
        """
        plt.figure(figsize=(12, 6))
        sns.histplot(self.df[column], kde=True, bins=50)
        plt.title(f"{column} 가격 분포")
        plt.show()
        
        print(f"📌 분산: {np.var(self.df[column])}")
        print(f"📌 왜도: {skew(self.df[column])}")
        print(f"📌 첨도: {kurtosis(self.df[column])}")

    def volatility_analysis(self, column='close'):
        """
        변동성 분석 (이동 평균, 지수이동평균, ATR)
        """
        self.df['MA_20'] = self.df[column].rolling(window=20).mean()
        self.df['EMA_20'] = self.df[column].ewm(span=20, adjust=False).mean()
        self.df['ATR'] = self.df['high'] - self.df['low']

        plt.figure(figsize=(12, 6))
        plt.plot(self.df[column], label="Close Price", alpha=0.5)
        plt.plot(self.df['MA_20'], label="MA 20", linestyle='dashed')
        plt.plot(self.df['EMA_20'], label="EMA 20", linestyle='dotted')
        plt.fill_between(self.df.index, self.df[column] - self.df['ATR'], self.df[column] + self.df['ATR'], color='gray', alpha=0.2, label="ATR")
        plt.legend()
        plt.title("📊 변동성 분석")
        plt.show()
    
    def market_microstructure_analysis(self):
        """
        시장 미세구조 분석 (호가창 기반 유동성 분석)
        """
        self.df['Bid-Ask Spread'] = self.df['ask_price_1'] - self.df['bid_price_1']
        plt.figure(figsize=(12, 6))
        plt.plot(self.df['Bid-Ask Spread'], label="Bid-Ask Spread")
        plt.legend()
        plt.title("📊 호가창 기반 스프레드 분석")
        plt.show()

# 사용 예시
# df = pd.read_csv("ohlcv_data.csv")
# analysis = StatisticalAnalysis(df)
# analysis.time_series_analysis()
# analysis.correlation_analysis()
# analysis.distribution_analysis()
# analysis.volatility_analysis()
# analysis.market_microstructure_analysis()
