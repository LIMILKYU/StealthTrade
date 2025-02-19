import websocket
import json
import time
from config import BINANCE_API_BASE

class WebSocketListener:
    def __init__(self, symbol="BTCUSDT"):
        self.ws_url = f"{BINANCE_API_BASE}/ws/{symbol.lower()}@depth"
        self.reconnect_delay = 5  # 재연결 대기 시간

    def on_message(self, ws, message):
        data = json.loads(message)
        print(f"📊 실시간 데이터 수신: {data}")

    def on_error(self, ws, error):
        print(f"❌ WebSocket 오류: {error}")
        self.reconnect()

    def on_close(self, ws, close_status_code, close_msg):
        print("🔴 WebSocket 연결 종료, 자동 재연결 시도...")
        self.reconnect()

    def on_open(self, ws):
        print("✅ WebSocket 연결 성공!")

    def reconnect(self):
        """ WebSocket 연결이 끊어지면 자동 재연결 """
        time.sleep(self.reconnect_delay)
        print("🔄 WebSocket 재연결 시도...")
        self.run()

    def run(self):
        while True:
            try:
                ws = websocket.WebSocketApp(self.ws_url,
                                            on_message=self.on_message,
                                            on_error=self.on_error,
                                            on_close=self.on_close)
                ws.on_open = self.on_open
                ws.run_forever()
            except Exception as e:
                print(f"⚠️ WebSocket 재연결 실패: {e}")
                time.sleep(self.reconnect_delay)

if __name__ == "__main__":
    listener = WebSocketListener(symbol="BTCUSDT")
    listener.run()
