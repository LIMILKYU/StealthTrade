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

    # ✅ Paper Trading 모드 (기본값: False)
    PAPER_TRADING = os.getenv("PAPER_TRADING", "False").lower() == "true"


    # 🔹 Telegram API 설정
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # 👈 여기에 봇 API 입력
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # 👈 여기에 본인의 Chat ID 입력

    # 🔹 매매할 코인 자동 선택 여부 (True: 자동, False: 수동 입력)
    AUTO_SELECT_COIN = os.getenv("AUTO_SELECT_COIN", "True").lower() == "true"

    # 🔹 사용자가 원하는 코인 입력 (수동 선택 시)
    USER_SELECTED_COINS = os.getenv("USER_SELECTED_COINS", "BTCUSDT,ETHUSDT").split(",")

    # 🔹 자동 선택 시 매매할 코인 개수 (1~10개)
    NUM_COINS_TO_TRADE = int(os.getenv("NUM_COINS_TO_TRADE", "3"))

    # ✅ tRPC API URL (프론트엔드 대시보드 연동)
    TRPC_API_URL = os.getenv("TRPC_API_URL")

    @staticmethod
    def get_balance():
        """ ✅ Binance API에서 내 계좌의 USDT 잔고 가져오기 """
        if Config.PAPER_TRADING:
            print("📌 [Paper Trading] 가상 잔고: 10,000 USDT")
            return 10000  # ✅ Paper Trading일 경우 Mock 데이터 반환

        if Config.BINANCE_API_KEY is None or Config.BINANCE_SECRET_KEY is None:
            print("🚨 [API 오류] Binance API 키가 없습니다!")
            return None

        url = f"{Config.BINANCE_BASE_URL}/api/v3/account"
        headers = {"X-MBX-APIKEY": Config.BINANCE_API_KEY}
        params = {"timestamp": int(time.time() * 1000)}

        # ✅ API 요청 서명 추가
        params["signature"] = Config.generate_signature(params)

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                account_info = response.json()
                for balance in account_info["balances"]:
                    if balance["asset"] == "USDT":  # ✅ USDT 잔고만 가져오기
                        return float(balance["free"])
            else:
                print(f"❌ [잔고 조회 실패] 응답 코드: {response.status_code} | 메시지: {response.text}")
                return None
        except Exception as e:
            print(f"❌ [API 오류] {e}")
            return None

    @staticmethod
    def get_all():
        """ ✅ 환경 변수 설정 확인 (디버깅 용도) """
        return {
            "BINANCE_API_KEY": "*****" if Config.BINANCE_API_KEY else None,
            "BINANCE_SECRET_KEY": "*****" if Config.BINANCE_SECRET_KEY else None,
            "BINANCE_BASE_URL": Config.BINANCE_BASE_URL,
            "PAPER_TRADING": Config.PAPER_TRADING,
            "TELEGRAM_BOT_TOKEN": "*****",
            "TELEGRAM_CHAT_ID": Config.TELEGRAM_CHAT_ID,
            "TRPC_API_URL": Config.TRPC_API_URL,
            "DEFAULT_TRADING_PAIR": Config.DEFAULT_TRADING_PAIR,
            "BALANCE": Config.get_balance()
        }

if __name__ == "__main__":
    print(Config.get_all())  # 환경 변수 확인
