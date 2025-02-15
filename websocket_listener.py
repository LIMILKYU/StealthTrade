import websocket
import json

# 메시지 수신 시 실행되는 함수
def on_message(ws, message):
    data = json.loads(message)
    print("📡 WebSocket 데이터 수신:", data)

# 오류 발생 시 실행되는 함수
def on_error(ws, error):
    print("⚠️ WebSocket 오류 발생:", error)

# 연결 종료 시 실행되는 함수
def on_close(ws, close_status_code, close_msg):
    print(f"🔌 WebSocket 연결 종료 - 상태 코드: {close_status_code}, 메시지: {close_msg}")

# 연결 성공 시 실행되는 함수
def on_open(ws):
    print("✅ WebSocket 연결 성공!")
    # WebSocket 구독 요청 (depth5, depth20, trade 데이터)
    subscribe_message = {
        "method": "SUBSCRIBE",
        "params": [
            "btcusdt@depth5",
            "btcusdt@depth20",
            "btcusdt@trade"
        ],
        "id": 1
    }
    ws.send(json.dumps(subscribe_message))

# WebSocket 실행
ws = websocket.WebSocketApp(
    "wss://stream.binance.com:9443/ws/btcusdt@depth5",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)
ws.on_open = on_open
ws.run_forever()
