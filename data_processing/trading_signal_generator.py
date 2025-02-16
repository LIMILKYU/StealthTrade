import pandas as pd
import numpy as np
import talib
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb

class SignalGenerator:
    def __init__(self, data: pd.DataFrame):
        """
        매매 신호 생성 클래스
        :param data: OHLCV 데이터 (open, high, low, close, volume)
        """
        self.data = data
        self.signals = pd.DataFrame(index=self.data.index)

    def apply_technical_indicators(self):
        """
        기술적 분석 기반 신호 생성
        """
        self.signals['SMA_50'] = talib.SMA(self.data['close'], timeperiod=50)
        self.signals['SMA_200'] = talib.SMA(self.data['close'], timeperiod=200)
        self.signals['RSI'] = talib.RSI(self.data['close'], timeperiod=14)
        self.signals['MACD'], _, _ = talib.MACD(self.data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        self.signals['Bollinger_Upper'], self.signals['Bollinger_Middle'], self.signals['Bollinger_Lower'] = talib.BBANDS(
            self.data['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    
    def apply_onchain_signals(self, whale_activity, exchange_flow):
        """
        온체인 데이터 기반 신호 생성
        :param whale_activity: 고래 매매 활동 데이터
        :param exchange_flow: 거래소 유입/유출 데이터
        """
        self.signals['whale_activity'] = whale_activity
        self.signals['exchange_flow'] = exchange_flow

    def apply_orderbook_signals(self, bid_ask_imbalance, iceberg_orders, trade_volume):
        """
        호가창 및 체결 데이터 기반 신호 생성
        :param bid_ask_imbalance: 매수/매도 불균형 지표
        :param iceberg_orders: Iceberg 주문 감지 데이터
        :param trade_volume: 거래량 데이터
        """
        self.signals['bid_ask_imbalance'] = bid_ask_imbalance
        self.signals['iceberg_orders'] = iceberg_orders
        self.signals['trade_volume'] = trade_volume

    def apply_ml_signals(self):
        """
        머신러닝 기반 신호 생성 (랜덤포레스트 & XGBoost)
        """
        features = self.signals.dropna()
        labels = np.where(features['SMA_50'] > features['SMA_200'], 1, 0)  # 예제: 골든크로스 기반 신호
        
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(features, labels)
        self.signals['RF_Prediction'] = rf_model.predict(features)
        
        xgb_model = xgb.XGBClassifier(n_estimators=100, use_label_encoder=False, eval_metric='logloss')
        xgb_model.fit(features, labels)
        self.signals['XGB_Prediction'] = xgb_model.predict(features)

    def get_signals(self):
        """
        최종 매매 신호 반환
        """
        return self.signals

# 사용 예제
# df = pd.read_csv('ohlcv_data.csv')  # OHLCV 데이터 불러오기
# sg = SignalGenerator(df)
# sg.apply_technical_indicators()
# sg.apply_ml_signals()
# final_signals = sg.get_signals()
# print(final_signals.head())
