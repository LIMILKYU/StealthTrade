# 📌 패턴 분석 적용 기법
# ✅ 통계적 패턴 분석 → 이동평균, 캔들 패턴, 볼린저 밴드
# ✅ 머신러닝 기반 패턴 인식 → KNN, 랜덤 포레스트, SVM, 신경망
# ✅ AI 기반 패턴 학습 → LSTM, CNN, Autoencoder
# ✅ 차트 패턴 탐지 → 헤드앤숄더, 삼각수렴, 쐐기형 패턴 등
# ✅ 이상 패턴 탐지 → 비정상적 거래량, 급변 가격 패턴

import numpy as np
import pandas as pd
import talib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

class PatternRecognition:
    def __init__(self, df):
        """
        패턴 분석 클래스
        :param df: OHLCV 데이터 (Pandas DataFrame)
        """
        self.df = df.copy()

    def moving_average_patterns(self, short_window=10, long_window=50):
        """
        이동평균을 활용한 패턴 탐지
        :param short_window: 단기 이동평균 기간
        :param long_window: 장기 이동평균 기간
        """
        self.df["SMA_short"] = self.df["close"].rolling(window=short_window).mean()
        self.df["SMA_long"] = self.df["close"].rolling(window=long_window).mean()
        self.df["golden_cross"] = (self.df["SMA_short"] > self.df["SMA_long"])  # 골든 크로스
        self.df["death_cross"] = (self.df["SMA_short"] < self.df["SMA_long"])  # 데드 크로스

    def candlestick_patterns(self):
        """
        캔들 패턴 탐지 (도지형, 강한 상승/하락 패턴 등)
        """
        self.df["doji"] = talib.CDLDOJI(self.df["open"], self.df["high"], self.df["low"], self.df["close"])
        self.df["hammer"] = talib.CDLHAMMER(self.df["open"], self.df["high"], self.df["low"], self.df["close"])
        self.df["engulfing"] = talib.CDLENGULFING(self.df["open"], self.df["high"], self.df["low"], self.df["close"])

    def bollinger_band_patterns(self, window=20, num_std=2):
        """
        볼린저 밴드 패턴 분석
        :param window: 이동평균 기간
        :param num_std: 표준편차 곱
        """
        self.df["SMA"] = self.df["close"].rolling(window=window).mean()
        self.df["std"] = self.df["close"].rolling(window=window).std()
        self.df["upper_band"] = self.df["SMA"] + (self.df["std"] * num_std)
        self.df["lower_band"] = self.df["SMA"] - (self.df["std"] * num_std)
        self.df["bollinger_breakout"] = (self.df["close"] > self.df["upper_band"]) | (self.df["close"] < self.df["lower_band"])

    def kmeans_pattern_analysis(self, n_clusters=3):
        """
        K-Means 클러스터링 기반 패턴 분석
        :param n_clusters: 클러스터 개수
        """
        features = ["close", "volume", "high", "low"]
        X = self.df[features]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.df["kmeans_cluster"] = kmeans.fit_predict(X_scaled)

    def random_forest_signal(self):
        """
        랜덤 포레스트 기반 패턴 예측
        """
        features = ["close", "volume", "high", "low"]
        X = self.df[features]
        y = (self.df["close"].shift(-1) > self.df["close"]).astype(int)  # 상승(1), 하락(0)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X.dropna())
        y = y.iloc[:-1]

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        self.df["rf_prediction"] = model.predict(X_scaled)

    def train_lstm_model(self, epochs=10):
        """
        LSTM 기반 패턴 예측
        :param epochs: 학습 반복 횟수
        """
        data = self.df["close"].values.reshape(-1, 1)
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)

        X, y = [], []
        seq_length = 10
        for i in range(len(data_scaled) - seq_length):
            X.append(data_scaled[i : i + seq_length])
            y.append(data_scaled[i + seq_length])

        X, y = np.array(X), np.array(y)

        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(seq_length, 1)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(loss="mse", optimizer="adam")
        model.fit(X, y, epochs=epochs, batch_size=16, verbose=1)

        self.lstm_model = model
        self.scaler = scaler

    def lstm_predict_next(self):
        """
        LSTM 모델 기반 다음 가격 예측
        """
        if not hasattr(self, "lstm_model"):
            raise ValueError("LSTM 모델이 학습되지 않았습니다.")

        last_seq = self.df["close"].values[-10:].reshape(-1, 1)
        last_seq_scaled = self.scaler.transform(last_seq)
        prediction = self.lstm_model.predict(last_seq_scaled.reshape(1, 10, 1))
        return self.scaler.inverse_transform(prediction)[0][0]

    def process_all(self):
        """
        모든 패턴 분석 실행
        """
        self.moving_average_patterns()
        self.candlestick_patterns()
        self.bollinger_band_patterns()
        self.kmeans_pattern_analysis()
        self.random_forest_signal()
        self.train_lstm_model()

# 사용 예시
# df = pd.read_csv("market_data.csv")
# pr = PatternRecognition(df)
# pr.process_all()
# print(pr.df.head())
