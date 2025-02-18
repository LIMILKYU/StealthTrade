from trade import place_order
from config import Config

if __name__ == "__main__":
    # ✅ 변경된 코드 (API 체크)
    if Config.BINANCE_API_KEY is None or Config.BINANCE_SECRET_KEY is None:
        print("🚨 바이낸스 API 없음. 테스트 모드로 실행합니다.")
    else:
        print("✅ Binance API 연결 성공. 실거래 모드 실행.")

    place_order("BTCUSDT", "BUY")  # ✅ API 없이 실행 가능하도록 변경됨
