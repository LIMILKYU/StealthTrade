# 📌 감성 분석 적용 기법
# ✅ 뉴스 기사 분석 → 특정 키워드(비트코인, 이더리움 등) 감성 점수 평가
# ✅ 트위터/소셜미디어 분석 → 실시간 트렌드 감성 분석
# ✅ Reddit & Telegram 데이터 분석 → 거래자들의 심리 파악
# ✅ AI 기반 감성 분석 → 자연어 처리(NLP)로 긍정/부정 감지
# ✅ 뉴스 속보 영향력 분석 → 특정 뉴스가 시장에 미치는 영향 측정

import requests
import json
import pandas as pd
import time
from textblob import TextBlob
from transformers import pipeline
import nltk
from bs4 import BeautifulSoup

# NLTK 필요 리소스 다운로드
nltk.download('punkt')

class SentimentAnalysis:
    def __init__(self, keywords=["Bitcoin", "Ethereum", "Crypto"]):
        """
        감성 분석 클래스
        :param keywords: 분석할 키워드 리스트
        """
        self.keywords = keywords
        self.sentiment_pipeline = pipeline("sentiment-analysis")
    
    def fetch_news(self):
        """
        뉴스 기사 크롤링 (Google 뉴스)
        """
        articles = []
        for keyword in self.keywords:
            url = f"https://news.google.com/search?q={keyword}&hl=en&gl=US&ceid=US:en"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            for item in soup.select("article"):
                title = item.select_one("h3").text if item.select_one("h3") else "No title"
                link = item.select_one("a")["href"] if item.select_one("a") else "#"
                articles.append({"title": title, "link": f"https://news.google.com{link}"})
                
            time.sleep(1)  # API 과부하 방지
        return articles

    def fetch_tweets(self, count=10):
        """
        트위터 감성 분석 (Twitter API 필요)
        """
        # 트위터 API를 사용하려면 Bearer Token 필요
        BEARER_TOKEN = "YOUR_TWITTER_BEARER_TOKEN"
        headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
        tweets = []

        for keyword in self.keywords:
            url = f"https://api.twitter.com/2/tweets/search/recent?query={keyword}&max_results={count}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                tweets.extend([tweet["text"] for tweet in data.get("data", [])])

        return tweets

    def analyze_sentiment(self, text):
        """
        텍스트 감성 분석 (긍정/부정/중립)
        """
        analysis = TextBlob(text)
        score = analysis.sentiment.polarity  # 감성 점수 (-1 ~ 1)
        sentiment = "Neutral"
        if score > 0.05:
            sentiment = "Positive"
        elif score < -0.05:
            sentiment = "Negative"
        return sentiment, score

    def analyze_with_transformers(self, text):
        """
        AI 기반 감성 분석 (Hugging Face BERT 모델 활용)
        """
        result = self.sentiment_pipeline(text)[0]
        return result["label"], result["score"]

    def process_sentiment(self):
        """
        전체 감성 분석 실행
        """
        news_data = self.fetch_news()
        tweet_data = self.fetch_tweets()

        news_sentiments = [{"title": news["title"], 
                            "sentiment": self.analyze_sentiment(news["title"])[0],
                            "score": self.analyze_sentiment(news["title"])[1]} 
                           for news in news_data]

        tweet_sentiments = [{"tweet": tweet, 
                             "sentiment": self.analyze_with_transformers(tweet)[0], 
                             "score": self.analyze_with_transformers(tweet)[1]} 
                            for tweet in tweet_data]

        return {"news_sentiment": pd.DataFrame(news_sentiments), 
                "tweet_sentiment": pd.DataFrame(tweet_sentiments)}

# 사용 예시
# sa = SentimentAnalysis()
# results = sa.process_sentiment()
# print(results["news_sentiment"].head())
# print(results["tweet_sentiment"].head())
