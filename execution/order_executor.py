#  거래소 API에서 계정 정보를 가져오고, AI 신호를 기반으로 최적화된 주문을 실행하는 코드

import requests
import logging
from strategy.trading_signal_generator import TradingSignalGenerator

class ExchangeAccount:
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://api.binance.com"):
        """
        거래소 API를 사용하여 자본금 및 포지션 데이터를 가져오는 클래스
        :param api_key: API 키
        :param secret_key: API 시크릿 키
        :param base_url: 거래소 API 기본 URL
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.headers = {"X-MBX-APIKEY": self.api_key}
        logging.basicConfig(level=logging.INFO)

    def get_account_balance(self):
        """ 내 계정의 총 자본금 및 잔액 조회 """
        url = f"{self.base_url}/api/v3/account"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            balances = {asset["asset"]: float(asset["free"]) for asset in data["balances"] if float(asset["free"]) > 0}
            logging.info(f"✅ 현재 계정 잔액: {balances}")
            return balances
        else:
            logging.error(f"❌ 계정 정보 조회 실패: {response.text}")
            return None

    def get_open_positions(self):
        """ 내 포지션 및 미결제약정(Open Interest) 조회 (선물 계정) """
        url = f"{self.base_url}/fapi/v2/positionRisk"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            positions = [pos for pos in response.json() if float(pos["positionAmt"]) != 0]
            logging.info(f"📊 현재 보유 포지션: {positions}")
            return positions
        else:
            logging.error(f"❌ 포지션 조회 실패: {response.text}")
            return None


class OrderExecutor:
    def __init__(self, api_key: str, secret_key: str, api_url: str, symbol: str):
        """
        주문 실행기 - AI 신호를 받아 주문 실행 + 레버리지 자동 조절
        :param api_key: API 키
        :param secret_key: API 시크릿 키
        :param api_url: 거래소 API URL
        :param symbol: 거래할 코인 심볼 (예: "BTCUSDT")
        """
        self.signal_generator = TradingSignalGenerator(api_url)
        self.exchange = ExchangeAccount(api_key, secret_key)
        self.symbol = symbol
        logging.basicConfig(level=logging.INFO)

    def adjust_leverage(self):
        """ 시장 상황을 고려한 레버리지 자동 조절 """
        positions = self.exchange.get_open_positions()
        if positions:
            for pos in positions:
                if pos["symbol"] == self.symbol:
                    current_leverage = int(pos["leverage"])
                    position_amt = float(pos["positionAmt"])
                    
                    # 강한 상승장: 레버리지 증가 (최대 10배)
                    if position_amt > 0:
                        new_leverage = min(current_leverage + 2, 10)
                    # 강한 하락장: 레버리지 최소화 (최소 1배)
                    else:
                        new_leverage = max(current_leverage - 2, 1)

                    logging.info(f"🔄 레버리지 조정: {current_leverage}배 → {new_leverage}배")
                    return new_leverage

        return 5  # 기본 레버리지 5배 설정

    def execute_trade(self):
        """ AI 최적화된 매매 신호를 받아 주문 실행 + 레버리지 자동 조절 """
        signal = self.signal_generator.generate_signal()
        if signal:
            leverage = self.adjust_leverage()  # 레버리지 자동 조절
            logging.info(f"✅ Executing AI Optimized Trade: {signal} (레버리지 {leverage}배)")

# 사용 예시
if __name__ == "__main__":
    API_KEY = "YOUR_BINANCE_API_KEY"
    SECRET_KEY = "YOUR_BINANCE_SECRET_KEY"
    SYMBOL = "BTCUSDT"
    API_URL = "https://api.binance.com/api/v3/ticker/24hr"
    
    executor = OrderExecutor(API_KEY, SECRET_KEY, API_URL, SYMBOL)
    executor.execute_trade()
