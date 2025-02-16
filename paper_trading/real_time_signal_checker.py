# 단순 이동평균(SMA) 기반 매매 신호 감지
# 추후 AI 기반 전략으로 확장 가능

import random

class RealTimeSignalChecker:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def get_signal(self):
        """ 랜덤 매매 신호 생성 (실제 데이터 기반으로 확장 가능) """
        return random.choice(["BUY", "SELL", None])

# 사용 예시
if __name__ == "__main__":
    signal_checker = RealTimeSignalChecker("BTCUSDT")
    print(signal_checker.get_signal())
