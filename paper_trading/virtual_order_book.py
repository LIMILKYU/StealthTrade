# 실제 호가창 데이터를 시뮬레이션하여 주문 체결 가능 여부 판단
# 현재 시장 가격을 제공하여 가상 거래 환경을 조성

import random

class VirtualOrderBook:
    def __init__(self, symbol: str):
        """
        가상 호가창 생성
        :param symbol: 거래할 코인 심볼
        """
        self.symbol = symbol
        self.current_price = 50000  # 예제 초기 가격

    def get_current_price(self):
        """ 현재 시장 가격 반환 (랜덤 변동) """
        self.current_price += random.uniform(-50, 50)  # 랜덤 가격 변동 (시뮬레이션)
        return round(self.current_price, 2)

# 사용 예시
if __name__ == "__main__":
    order_book = VirtualOrderBook("BTCUSDT")
    print(order_book.get_current_price())
