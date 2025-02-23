import websocket
import json
import numpy as np
import threading
import logging
import pandas as pd

class MarketMicrostructureAnalyzer:
    def __init__(self, symbol, selected_coins=None):
        self.symbol = symbol.lower()
        self.selected_coins = selected_coins if selected_coins else [self.symbol]
        self.order_book = {"bids": [], "asks": []}
        self.trade_data = []
        self.lock = threading.Lock()

        # WebSocket 연결 설정
        self.ws = None
        self.connect_websocket()

    def connect_websocket(self):
        """ Binance WebSocket 연결 (depth100ms 및 trade 데이터 처리) """
        url = f"wss://stream.binance.com:9443/ws/"
        symbols = [f"{coin}@depth100ms/{coin}@trade" for coin in self.selected_coins]
        url += '/'.join(symbols)
        self.ws = websocket.WebSocketApp(url,
                                         on_message=self.on_message,
                                         on_close=self.on_close,
                                         on_error=self.on_error)
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

    def on_message(self, ws, message):
        """ WebSocket 메시지 처리 (호가창 + 체결 데이터 수집) """
        data = json.loads(message)
        with self.lock:
            if "bids" in data and "asks" in data:
                self.order_book["bids"] = [(float(price), float(size)) for price, size in data["bids"][:100]]
                self.order_book["asks"] = [(float(price), float(size)) for price, size in data["asks"][:100]]

            elif "e" in data and data["e"] == "trade":
                self.trade_data.append({
                    "price": float(data["p"]),
                    "quantity": float(data["q"]),
                    "is_buyer_maker": data["m"],  # True: 매수 체결, False: 매도 체결
                    "timestamp": data["T"]
                })

    def on_close(self, ws, close_status_code, close_msg):
        """ WebSocket 연결 종료 처리 """
        logging.info(f"❌ WebSocket 연결 종료: {self.symbol}")

    def on_error(self, ws, error):
        """ WebSocket 오류 처리 """
        logging.error(f"⚠️ WebSocket 오류 발생: {error}")

    def calculate_order_flow(self):
        """ 주문 흐름 분석 (매수/매도 압력) """
        buy_pressure = sum([size for price, size in self.order_book["bids"]])
        sell_pressure = sum([size for price, size in self.order_book["asks"]])

        return buy_pressure, sell_pressure

    def get_trade_data(self):
        """ 수집된 체결 데이터 반환 """
        return pd.DataFrame(self.trade_data)

# ✅ 사용 예시
if __name__ == "__main__":
    analyzer = MarketMicrostructureAnalyzer(symbol="BTCUSDT", selected_coins=["BTCUSDT", "ETHUSDT"])
    print("WebSocket 연결 시작...")
