import logging
from ai_optimization.ai_real_time_optimizer import AIRealTimeOptimizer

class TradingSignalGenerator:
    def __init__(self, api_url: str, selected_coins: list = ["BTCUSDT"]):
        self.ai_optimizer = AIRealTimeOptimizer(api_url)
        self.selected_coins = selected_coins  # 다중 코인 지원
        logging.basicConfig(level=logging.INFO)

    def generate_signal(self):
        """ AI 실시간 최적화된 매매 신호 반환 """
        signals = {}
        for coin in self.selected_coins:
            signal = self.ai_optimizer.update_strategy(coin)
            signals[coin] = signal
        return signals

# 사용 예시
if __name__ == "__main__":
    signal_generator = TradingSignalGenerator("https://api.binance.com/api/v3/ticker/24hr", selected_coins=["BTCUSDT", "ETHUSDT"])
    signals = signal_generator.generate_signal()
    print(f"📈 생성된 AI 최적화 매매 신호: {signals}")
