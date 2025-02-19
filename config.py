import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """ StealthTrader 환경 변수 설정 """

    # ✅ 변경된 코드 (API 기본 URL 추가)
    BINANCE_BASE_URL = "https://api.binance.com"

    # Binance API 정보
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

    # ✅ 변경된 코드 (API 없이 실행 가능)
    if BINANCE_API_KEY is None or BINANCE_SECRET_KEY is None:
        print("🚨 Binance API 없음 → 테스트 모드로 실행")
        BINANCE_API_KEY = None
        BINANCE_SECRET_KEY = None

    # ✅ Paper Trading 모드
    PAPER_TRADING = os.getenv("PAPER_TRADING", "False").lower() == "true"

    # ✅ 변경된 코드 (OPENAI API 기본값 설정)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_default_key_here")

    # Telegram 알림 설정
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # tRPC API URL (프론트엔드 대시보드 연동)
    TRPC_API_URL = os.getenv("TRPC_API_URL")

    # 기본 매매 대상 코인
    DEFAULT_TRADING_PAIR = os.getenv("DEFAULT_TRADING_PAIR", "BTCUSDT")

    @staticmethod
    def get_all():
        """ 환경 변수 설정 확인 (디버깅 용도) """
        return {
            "BINANCE_API_KEY": "*****" if Config.BINANCE_API_KEY else None,
            "BINANCE_SECRET_KEY": "*****" if Config.BINANCE_SECRET_KEY else None,
            "BINANCE_BASE_URL": Config.BINANCE_BASE_URL,
            "PAPER_TRADING": Config.PAPER_TRADING,
            "OPENAI_API_KEY": "*****",
            "TELEGRAM_BOT_TOKEN": "*****",
            "TELEGRAM_CHAT_ID": Config.TELEGRAM_CHAT_ID,
            "TRPC_API_URL": Config.TRPC_API_URL,
            "DEFAULT_TRADING_PAIR": Config.DEFAULT_TRADING_PAIR
        }

if __name__ == "__main__":
    print(Config.get_all())  # 환경 변수 설정 확인
