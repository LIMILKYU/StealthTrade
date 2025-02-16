# LSTM을 활용한 가격 예측 (ai_prediction.py)

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset

# 🔥 1. LSTM 모델 정의
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

# 🔥 2. 데이터 준비
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

# 🔥 3. 모델 학습
def train_model(csv_path, epochs=50, batch_size=32, learning_rate=0.001):
    X, y, scaler = load_data(csv_path)
    dataset = TensorDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = LSTM_Predictor().cuda()
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

        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.6f}")

    torch.save(model.state_dict(), "lstm_trading_model.pth")
    print("✅ 모델 학습 완료!")
    return model, scaler

# 🔥 4. 가격 예측
def predict_price(model, csv_path, sequence_length=60):
    X, _, scaler = load_data(csv_path, sequence_length)
    model.load_state_dict(torch.load("lstm_trading_model.pth"))
    model.eval()

    with torch.no_grad():
        X = X[-1].unsqueeze(0).cuda()
        predicted_price = model(X).cpu().numpy()
        predicted_price = scaler.inverse_transform(predicted_price.reshape(-1, 1))

    return predicted_price[0][0]

if __name__ == "__main__":
    train_model("price_data.csv")
    predicted_price = predict_price(LSTM_Predictor().cuda(), "price_data.csv")
    print(f"📈 AI 예측 가격: {predicted_price:.2f}")
