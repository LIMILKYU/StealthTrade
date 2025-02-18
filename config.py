import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """ StealthTrade 프로젝트의 환경 변수를 관리하는 클래스 """

    # Binance API 정보
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

    # ✅ 변경된 코드 (API 없이 실행 가능)
    if BINANCE_API_KEY is None or BINANCE_SECRET_KEY is None:
        print("🚨 Binance API 없음 → 테스트 모드로 실행")
        BINANCE_API_KEY = None
        BINANCE_SECRET_KEY = None

    # 🔹 Paper Trading 모드 (API 없이 실행 가능)
    PAPER_TRADING = os.getenv("PAPER_TRADING", "False").lower() == "true"

    @staticmethod
    def get_all():
        """ 환경 변수 설정 확인 (디버깅 용도) """
        return {
            "BINANCE_API_KEY": "*****" if Config.BINANCE_API_KEY else None,
            "BINANCE_SECRET_KEY": "*****" if Config.BINANCE_SECRET_KEY else None,
            "PAPER_TRADING": Config.PAPER_TRADING
        }

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
            "BINANCE_API_KEY": Config.BINANCE_API_KEY[:5] + "*****",  # 보안상 일부만 출력
            "BINANCE_SECRET_KEY": "*****",
            "TELEGRAM_BOT_TOKEN": "*****",
            "TELEGRAM_CHAT_ID": Config.TELEGRAM_CHAT_ID,
            "TRPC_API_URL": Config.TRPC_API_URL,
            "DEFAULT_TRADING_PAIR": Config.DEFAULT_TRADING_PAIR
        }

if __name__ == "__main__":
    print(Config.get_all())  # 환경 변수 설정 확인
