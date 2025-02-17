import os
from dotenv import load_dotenv

# 🔹 .env 파일 로드
load_dotenv()

# 🔹 환경 변수 설정
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
BINANCE_BASE_URL = "https://api.binance.com"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 🔹 매매할 코인 자동 선택 여부 (True: 자동, False: 수동 입력)
AUTO_SELECT_COIN = os.getenv("AUTO_SELECT_COIN", "True").lower() == "true"

# 🔹 사용자가 원하는 코인 입력 (수동 선택 시)
USER_SELECTED_COINS = os.getenv("USER_SELECTED_COINS", "BTCUSDT,ETHUSDT").split(",")

# 🔹 자동 선택 시 매매할 코인 개수 (1~10개)
NUM_COINS_TO_TRADE = int(os.getenv("NUM_COINS_TO_TRADE", "3"))
