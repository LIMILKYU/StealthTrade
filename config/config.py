import os
from dotenv import load_dotenv

# 🔹 .env 파일 로드
load_dotenv()

class Config:
    """ StealthTrader 프로젝트의 환경 변수를 관리하는 클래스 """

    # 🔹 Binance API 정보
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
    BINANCE_BASE_URL = "https://api.binance.com"

    # 🔹 Telegram API 설정
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # 👈 여기에 봇 API 입력
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # 👈 여기에 본인의 Chat ID 입력

    # 🔹 매매할 코인 자동 선택 여부 (True: 자동, False: 수동 입력)
    AUTO_SELECT_COIN = os.getenv("AUTO_SELECT_COIN", "True").lower() == "true"

    # 🔹 사용자가 원하는 코인 입력 (수동 선택 시)
    USER_SELECTED_COINS = os.getenv("USER_SELECTED_COINS", "BTCUSDT,ETHUSDT").split(",")

    # 🔹 자동 선택 시 매매할 코인 개수 (1~10개)
    NUM_COINS_TO_TRADE = int(os.getenv("NUM_COINS_TO_TRADE", "3"))

    @staticmethod
    def get_all():
        """ 환경 변수 설정 확인 (디버깅 용도) """
        return {
            "BINANCE_API_KEY": "*****",
            "BINANCE_SECRET_KEY": "*****",
            "BINANCE_BASE_URL": Config.BINANCE_BASE_URL,
            "TELEGRAM_BOT_TOKEN": "*****",
            "TELEGRAM_CHAT_ID": Config.TELEGRAM_CHAT_ID,
            "AUTO_SELECT_COIN": Config.AUTO_SELECT_COIN,
            "USER_SELECTED_COINS": Config.USER_SELECTED_COINS,
            "NUM_COINS_TO_TRADE": Config.NUM_COINS_TO_TRADE,
        }

if __name__ == "__main__":
    print(Config.get_all())  # 환경 변수 확인
