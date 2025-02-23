import os
import logging
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """ StealthTrader 환경 변수 설정 """

    # ✅ Binance API 설정
    BINANCE_BASE_URL = "https://api.binance.com"
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

    if not BINANCE_API_KEY or not BINANCE_SECRET_KEY:
        logger.warning("🚨 Binance API 없음 → 테스트 모드로 실행")
        BINANCE_API_KEY = None
        BINANCE_SECRET_KEY = None

    # ✅ Paper Trading 모드 (Boolean 변환)
    PAPER_TRADING = os.getenv("PAPER_TRADING", "False").strip().lower() == "true"

    # ✅ OpenAI API 키 기본값 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_default_key_here")

    # ✅ Telegram 알림 설정
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0")) if os.getenv("TELEGRAM_CHAT_ID") else None

    # ✅ tRPC API URL (프론트엔드 대시보드 연동)
    TRPC_API_URL = os.getenv("TRPC_API_URL") or None

    # ✅ 기본 매매 대상 코인
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
            "TELEGRAM_BOT_TOKEN": "*****" if Config.TELEGRAM_BOT_TOKEN else None,
            "TELEGRAM_CHAT_ID": Config.TELEGRAM_CHAT_ID,
            "TRPC_API_URL": Config.TRPC_API_URL,
            "DEFAULT_TRADING_PAIR": Config.DEFAULT_TRADING_PAIR
        }

if __name__ == "__main__":
    logger.info("환경 변수 설정 확인:")
    print(Config.get_all())
