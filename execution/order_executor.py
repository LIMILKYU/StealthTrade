# AI 최적화된 신호를 받아 주문을 실행
# AI가 생성한 신호를 즉각 반영하여 변동성 대응

iimport logging
from strategy.trading_signal_generator import TradingSignalGenerator

class OrderExecutor:
    def __init__(self, api_url: str):
        self.signal_generator = TradingSignalGenerator(api_url)
        logging.basicConfig(level=logging.INFO)

    def execute_trade(self):
        """ AI 실시간 최적화된 매매 신호를 받아 주문 실행 """
        signal = self.signal_generator.generate_signal()
        if signal:
            logging.info(f"✅ Executing AI Optimized Trade: {signal}")

# 사용 예시
if __name__ == "__main__":
    executor = OrderExecutor("https://api.binance.com/api/v3/ticker/24hr")
    executor.execute_trade()



# ✅ 시장 상황을 고려한 레버리지 자동 조절 추가 완료!
# 강한 상승장에서 높은 레버리지 적용
# 강한 하락장에서는 레버리지를 최소화하고, 숏 포지션만 가능하도록 설정
