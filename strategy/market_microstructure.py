import websocket
import json
import numpy as np
import threading
import time

class MarketMicrostructureAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol.lower()
        self.order_book = {"bids": [], "asks": []}
        self.trade_data = []
        self.lock = threading.Lock()

        # ✅ Binance WebSocket 연결 (depth100 추가)
        self.ws = None
        self.connect_websocket()

    def connect_websocket(self):
        """ ✅ Binance WebSocket 연결 (depth100 적용) """
        url = f"wss://stream.binance.com:9443/ws/{self.symbol}@depth100ms/{self.symbol}@trade"
        self.ws = websocket.WebSocketApp(url,
                                         on_message=self.on_message,
                                         on_close=self.on_close,
                                         on_error=self.on_error)
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

    def on_message(self, ws, message):
        """ ✅ WebSocket 메시지 처리 (호가창 + 체결 데이터 수집) """
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
        print(f"❌ WebSocket 연결 종료: {self.symbol}")

    def on_error(self, ws, error):
        """ WebSocket 오류 처리 """
        print(f"⚠️ WebSocket 오류 발생: {error}")

    def calculate_order_flow_imbalance(self):
        """ ✅ 실시간 Order Flow Imbalance 계산 (depth100 적용) """
        with self.lock:
            if not self.order_book["bids"] or not self.order_book["asks"]:
                return 0  # 데이터 부족 시 0 반환

            total_bid_vol = sum([size for _, size in self.order_book["bids"][:100]])  # 상위 100개 매수 호가
            total_ask_vol = sum([size for _, size in self.order_book["asks"][:100]])  # 상위 100개 매도 호가

            imbalance = (total_bid_vol - total_ask_vol) / (total_bid_vol + total_ask_vol)
            return imbalance

    def detect_iceberg_orders(self):
        """ ✅ Iceberg 주문 감지 (depth100에서 대량 미체결 주문 감지) """
        with self.lock:
            iceberg_detected = False
            for _, size in self.order_book["bids"] + self.order_book["asks"]:
                if size > 1000:  # ✅ 기존보다 더 높은 임계값 적용 (대량 주문 감지 정확도 향상)
                    iceberg_detected = True
                    break
            return iceberg_detected

    def detect_hft_activity(self):
        """ ✅ HFT(고빈도 트레이딩) 감지 (매매 빈도 및 속도 분석) """
        with self.lock:
            if len(self.trade_data) < 50:
                return "약함"  # 데이터 부족 시 기본값

            last_trades = self.trade_data[-50:]  # 최근 50개 체결 데이터
            time_diffs = [last_trades[i]["timestamp"] - last_trades[i - 1]["timestamp"] for i in range(1, len(last_trades))]
            avg_time_diff = np.mean(time_diffs) if time_diffs else 1000  # 평균 체결 간격 (ms)

            if avg_time_diff < 50:  # ✅ 50ms 이하의 빠른 체결 발생 시 HFT 강함
                return "강함"
            return "약함"

    def analyze_market(self):
        """ ✅ 시장 미세구조 분석 결과 반환 """
        return {
            "OrderFlowImbalance": self.calculate_order_flow_imbalance(),
            "IcebergDetected": self.detect_iceberg_orders(),
            "HFTActivity": self.detect_hft_activity(),
        }

if __name__ == "__main__":
    symbol = "btcusdt"
    analyzer = MarketMicrostructureAnalyzer(symbol)

    while True:
        time.sleep(5)
        market_signal = analyzer.analyze_market()
        print(f"📊 [실시간 시장 분석] {market_signal}")
