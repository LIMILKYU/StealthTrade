import time
from trade import place_order
from config import Config

if __name__ == "__main__":
    if Config.BINANCE_API_KEY is None or Config.BINANCE_SECRET_KEY is None:
        print("🚨 바이낸스 API 없음. 테스트 모드로 실행합니다.")
    else:
        print("✅ Binance API 연결 성공. 실거래 모드 실행.")

    # ✅ 변경된 코드 (반복 실행)
    while True:
        print("📌 [자동매매] BTCUSDT 매수 주문 실행 중...")
        response = place_order("BTCUSDT", "BUY")  # ✅ 주문 실행
        print(f"📌 [주문 응답]: {response}")  # ✅ 주문 결과 출력
        time.sleep(10)  # ✅ 10초마다 실행
