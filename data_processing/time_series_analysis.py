# 📌 시계열 분석 주요 목표
# ✅ 고전적 시계열 모델 적용 (ARIMA, GARCH 등)
# ✅ 딥러닝 기반 시계열 예측 (LSTM, Transformer 활용 가능)
# ✅ 자기상관성 분석 (ACF, PACF) → 최적 모델 선택
# ✅ 파생 지표 (파워 스펙트럼, 퓨리에 변환) 분석 → 패턴 감지
# ✅ 멀티타임프레임 데이터 활용 (틱 데이터 ~ 일봉까지)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler
from ohlcv_collector import OHLCVCollector  # OHLCV 데이터 수집 모듈

class TimeSeriesAnalysis:
    def __init__(self, asset="BTCUSDT", interval="1h", use_lstm=False):
        """
        시계열 분석 클래스
        :param asset: 분석할 자산 (예: BTCUSDT)
        :param interval: 데이터 간격 (예: "1h", "15m")
        :param use_lstm: LSTM 모델을 사용할지 여부
        """
        self.asset = asset
        self.interval = interval
        self.use_lstm = use_lstm
        self.price_collector = OHLCVCollector()
        self.scaler = MinMaxScaler(feature_range=(-1, 1))

    def fetch_data(self, lookback=500):
        """
        시계열 분석을 위한 데이터 수집
        """
        df = self.price_collector.get_ohlcv(self.asset, self.interval, lookback)
        df['returns'] = df['close'].pct_change()
        return df.dropna()

    def stationarity_test(self, df):
        """
        ADF 검정을 통한 정상성(Stationarity) 테스트
        """
        result = adfuller(df["close"])
        return {"ADF Statistic": result[0], "p-value": result[1]}

    def plot_acf_pacf(self, df):
        """
        자기상관함수(ACF) 및 부분자기상관(PACF) 분석
        """
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        sns.lineplot(x=range(len(df)), y=acf(df["returns"], nlags=30), ax=axes[0])
        sns.lineplot(x=range(len(df)), y=pacf(df["returns"], nlags=30), ax=axes[1])
        axes[0].set_title("자기상관함수 (ACF)")
        axes[1].set_title("부분자기상관함수 (PACF)")
        plt.show()

    def arima_model(self, df):
        """
        ARIMA 모델을 사용한 시계열 예측
        """
        model = ARIMA(df["close"], order=(5,1,0))
        result = model.fit()
        return result.summary()

    def garch_model(self, df):
        """
        GARCH 모델을 사용한 변동성 예측
        """
        model = arch_model(df["returns"].dropna() * 100, vol="Garch", p=1, q=1)
        result = model.fit(disp="off")
        return result.summary()

    def preprocess_lstm(self, df, lookback=50):
        """
        LSTM을 위한 데이터 전처리
        """
        data = self.scaler.fit_transform(df[['close']].values)
        x_train, y_train = [], []
        for i in range(lookback, len(data)):
            x_train.append(data[i-lookback:i, 0])
            y_train.append(data[i, 0])
        return torch.tensor(x_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.float32)

    def train_lstm(self, df, lookback=50, epochs=20, batch_size=32):
        """
        LSTM을 활용한 시계열 예측 모델 훈련
        """
        class LSTMModel(nn.Module):
            def __init__(self):
                super(LSTMModel, self).__init__()
                self.lstm = nn.LSTM(input_size=1, hidden_size=50, num_layers=2, batch_first=True)
                self.fc = nn.Linear(50, 1)

            def forward(self, x):
                h0 = torch.zeros(2, x.size(0), 50)
                c0 = torch.zeros(2, x.size(0), 50)
                out, _ = self.lstm(x.unsqueeze(2), (h0, c0))
                return self.fc(out[:, -1, :])

        x_train, y_train = self.preprocess_lstm(df, lookback)
        model = LSTMModel()
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = model(x_train)
            loss = criterion(outputs.squeeze(), y_train)
            loss.backward()
            optimizer.step()
            if epoch % 5 == 0:
                print(f"Epoch {epoch}: Loss {loss.item()}")

        return model

    def run_analysis(self):
        """
        시계열 분석 실행
        """
        df = self.fetch_data()
        print("📊 데이터 정상성 검정 (ADF Test) 결과:")
        print(self.stationarity_test(df))

        print("\n📊 ARIMA 모델 결과:")
        print(self.arima_model(df))

        print("\n📊 GARCH 모델 결과:")
        print(self.garch_model(df))

        if self.use_lstm:
            print("\n📊 LSTM 모델 학습 중...")
            lstm_model = self.train_lstm(df)
            return lstm_model
        else:
            self.plot_acf_pacf(df)
            return None

# 실행 예제
# ts = TimeSeriesAnalysis(use_lstm=True)
# ts.run_analysis()
