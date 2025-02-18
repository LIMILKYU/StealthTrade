import logging

def calculate_optimal_execution_price(order_book, trade_type, order_size):
    """
    슬리피지를 최소화하는 최적 체결 가격을 계산
    - order_book: 현재 호가창 데이터
    - trade_type: "buy" 또는 "sell"
    - order_size: 주문량
    """
    try:
        if trade_type == "buy":
            # 매수 시 최적 체결가 계산 (호가창 분석)
            best_price = min(order_book["asks"], key=lambda x: x[0])[0]
        else:
            # 매도 시 최적 체결가 계산
            best_price = max(order_book["bids"], key=lambda x: x[0])[0]

        return best_price
    except Exception as e:
        logging.error(f"슬리피지 최적 체결가 계산 오류: {e}")
        return None
