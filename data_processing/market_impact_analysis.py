# 📌 시장 영향 분석 주요 목표
# ✅ 뉴스 & 트위터 감성이 가격 변동에 미치는 영향 분석
# ✅ 감성 점수 vs. 가격 변동률 상관관계 측정
# ✅ 이벤트 발생 전후 시장 변동성 비교 (Event Study Analysis)
# ✅ 머신러닝 기반 예측 모델 구축 (감성 점수 → 가격 변동 예측)
# ✅ VWAP, 거래량과 감성 지표 결합하여 최적 매매 전략 개발

import pandas as pd
import numpy as np
import requests
import time
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
from sentiment_analysis import SentimentAnalysis  # 감성 분석 모듈 사용
from ohlcv_collector import OHLCVCollector  # 가격 데이터 수집 모듈

class MarketImpactAnalysis:
    def __init__(self, asset="BTCUSDT", interval="1h"):
        """
        시장 영향 분석 클래스
        :param asset: 분석할 암호화폐 (예: BTCUSDT)
        :param interval: 가격 데이터 간격 (예: "1h", "15m")
        """
        self.asset = asset
        self.interval = interval
        self.sentiment_analyzer = SentimentAnalysis()
        self.price_collector = OHLCVCollector()
    
    def fetch_price_data(self, lookback=50):
        """
        지정된 자산의 가격 데이터 수집 (최근 50개 캔들)
        """
        return self.price_collector.get_ohlcv(self.asset, self.interval, lookback)

    def compute_price_change(self, df):
        """
        가격 변화율 계산 (전 캔들 대비 % 변화)
        """
        df["price_change"] = df["close"].pct_change() * 100
        return df

    def merge_sentiment_price(self):
        """
        감성 점수와 가격 변동 데이터 결합
        """
        price_data = self.fetch_price_data()
        sentiment_data = self.sentiment_analyzer.process_sentiment()

        # 데이터 전처리
        price_data = self.compute_price_change(price_data)
        sentiment_data["news_sentiment"]["timestamp"] = pd.to_datetime("now")
        sentiment_data["tweet_sentiment"]["timestamp"] = pd.to_datetime("now")

        # 시간 기준으로 병합
        combined = price_data.merge(sentiment_data["news_sentiment"], how="left", left_index=True, right_index=True)
        combined = combined.merge(sentiment_data["tweet_sentiment"], how="left", left_index=True, right_index=True)

        # 결측값 처리
        combined.fillna(0, inplace=True)
        return combined

    def correlation_analysis(self, df):
        """
        감성 점수와 가격 변동률 간의 상관관계 분석
        """
        news_corr, _ = pearsonr(df["score_x"], df["price_change"])
        tweet_corr, _ = pearsonr(df["score_y"], df["price_change"])

        print(f"뉴스 감성 점수와 가격 변동 상관계수: {news_corr:.4f}")
        print(f"트윗 감성 점수와 가격 변동 상관계수: {tweet_corr:.4f}")

        return {"news_correlation": news_corr, "tweet_correlation": tweet_corr}

    def linear_regression_analysis(self, df):
        """
        감성 점수 → 가격 변동률 예측 (선형 회귀 모델)
        """
        X = df[["score_x", "score_y"]]  # 뉴스 및 트윗 감성 점수
        y = df["price_change"]

        model = LinearRegression()
        model.fit(X, y)
        score = model.score(X, y)

        print(f"선형 회귀 예측 정확도 (R²): {score:.4f}")
        return model

    def plot_impact_analysis(self, df):
        """
        감성 분석과 가격 변화 시각화
        """
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x=df.index, y="price_change", label="Price Change", color="blue")
        sns.lineplot(data=df, x=df.index, y="score_x", label="News Sentiment", color="green")
        sns.lineplot(data=df, x=df.index, y="score_y", label="Tweet Sentiment", color="red")
        plt.title("감성 분석과 시장 변동 관계")
        plt.xlabel("시간")
        plt.ylabel("변화율 (%)")
        plt.legend()
        plt.show()

    def run_analysis(self):
        """
        전체 시장 영향 분석 실행
        """
        df = self.merge_sentiment_price()
        correlation_results = self.correlation_analysis(df)
        regression_model = self.linear_regression_analysis(df)
        self.plot_impact_analysis(df)

        return {"correlation_results": correlation_results, "regression_model": regression_model}

# 실행 예제
# mia = MarketImpactAnalysis()
# mia.run_analysis()
