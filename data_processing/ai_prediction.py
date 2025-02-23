import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
from torch.utils.data import DataLoader, TensorDataset
import os
from pymongo import MongoClient
import mysql.connector
import psycopg2
from dotenv import load_dotenv

# ✅ 환경 변수 로드
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "trading_data")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "ai_predictions")
SELECTED_COINS = os.getenv("SELECTED_COINS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")
USE_MYSQL = os.getenv("USE_MYSQL") == "True"
USE_POSTGRES = os.getenv("USE_POSTGRES") == "True"
USE_MONGO = os.getenv("USE_MONGO") == "True"

class LSTM_Predictor(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=2, output_size=1):
        super(LSTM_Predictor, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

def load_data(csv_path, sequence_length=60):
    df = pd.read_csv(csv_path)
    prices = df["Close"].values.reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(0, 1))
    prices_scaled = scaler.fit_transform(prices)

    X, y = [], []
    for i in range(len(prices_scaled) - sequence_length):
        X.append(prices_scaled[i:i+sequence_length])
        y.append(prices_scaled[i+sequence_length])

    X, y = np.array(X), np.array(y)
    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32), scaler

def train_model(csv_path, epochs=50, batch_size=32, learning_rate=0.001, hidden_size=50, num_layers=2):
    X, y, scaler = load_data(csv_path)
    dataset = TensorDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = LSTM_Predictor(hidden_size=hidden_size, num_layers=num_layers).cuda()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    print("🚀 LSTM 모델 훈련 시작...")
    for epoch in range(epochs):
        for batch_X, batch_y in dataloader:
            batch_X, batch_y = batch_X.cuda(), batch_y.cuda()
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

    # 모델 저장
    torch.save(model.state_dict(), "lstm_model.pth")
    print("🚀 모델 훈련 완료! 모델 저장됨.")
    return model, scaler

def time_series_cross_validation(csv_path, sequence_length=60, epochs=50, batch_size=32, learning_rate=0.001):
    X, y, scaler = load_data(csv_path, sequence_length)
    tscv = TimeSeriesSplit(n_splits=5)
    
    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        print(f"\n🚀 Cross-validation Fold {fold+1}...")
        
        train_X, test_X = X[train_idx], X[test_idx]
        train_y, test_y = y[train_idx], y[test_idx]

        train_dataset = TensorDataset(train_X, train_y)
        test_dataset = TensorDataset(test_X, test_y)
        
        train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

        model = LSTM_Predictor().cuda()
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)

        for epoch in range(epochs):
            model.train()
            for batch_X, batch_y in train_dataloader:
                batch_X, batch_y = batch_X.cuda(), batch_y.cuda()
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

        model.eval()
        total_loss = 0
        with torch.no_grad():
            for batch_X, batch_y in test_dataloader:
                batch_X, batch_y = batch_X.cuda(), batch_y.cuda()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                total_loss += loss.item()

        print(f"Fold {fold+1} Test Loss: {total_loss / len(test_dataloader):.4f}")

# ✅ 사용 예시
if __name__ == "__main__":
    csv_path = "ohlcv_data.csv"  # 예시 데이터 경로
    time_series_cross_validation(csv_path)
