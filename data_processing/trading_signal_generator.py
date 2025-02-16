import numpy as np
import pandas as pd
from auto_ml_optimizer import AutoMLModel
from technical_indicator import calculate_indicators
from pattern_recognition import detect_patterns
from sentiment_analysis import analyze_sentiment
from time_series_analysis import forecast_trend
from market_impact_analysis import assess_market_impact
from volatility_analysis import compute_volatility
from statistical_analysis import evaluate_statistics

class TradingSignalGenerator:
    def __init__(self, data):
        """
        매매 신호 생성 클래스
        :param data: 시장 데이터 (DataFrame 형식)
        """
        self.data = data
        self.model = AutoMLModel()
        self.signals = pd.DataFrame(index=self.data.index)
    
    def generate_signals(self):
        """
        매매 신호 생성 (통계적 분석 + AI 기반 분석 결합)
        """
        # 1️⃣ 기술적 지표 계산
        indicators = calculate_indicators(self.data)
        
        # 2️⃣ 패턴 인식 (캔들 패턴, 추세 분석)
        patterns = detect_patterns(self.data)
        
        # 3️⃣ 감성 분석 (뉴스, 트위터 등 외부 데이터 반영 가능)
        sentiment_scores = analyze_sentiment(self.data)
        
        # 4️⃣ 시계열 예측 (AutoML 모델 활용)
        trend_forecast = forecast_trend(self.data)
        
        # 5️⃣ 시장 영향 분석 (대량 주문, Bid-Ask Imbalance 등)
        market_impact = assess_market_impact(self.data)
        
        # 6️⃣ 변동성 분석 (ATR, Bollinger Bands 등)
        volatility = compute_volatility(self.data)
        
        # 7️⃣ 통계적 분석 (평균 회귀 전략 등 적용 가능)
        statistics = evaluate_statistics(self.data)
        
        # 8️⃣ AutoML 기반 최적 모델 활용하여 최종 매매 신호 생성
        features = pd.concat([indicators, patterns, sentiment_scores, trend_forecast, market_impact, volatility, statistics], axis=1)
        self.signals['signal'] = self.model.predict(features)
        
        return self.signals
    
    def get_signals(self):
        """
        생성된 매매 신호 반환
        """
        return self.signals

# 사용 예시
# data = pd.read_csv('market_data.csv')  # 시장 데이터 로드
# signal_generator = TradingSignalGenerator(data)
# signals = signal_generator.generate_signals()
# print(signals)
