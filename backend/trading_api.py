import logging
from trpc.server import TRPCRouter
from execution.real_time_trading import execute_trade

# 로깅 설정
logger = logging.getLogger(__name__)

class TradingAPI(TRPCRouter):
    async def place_order(self, order_type: str, symbol: str, quantity: float):
        """
        웹 대시보드에서 매매 요청을 받아 자동매매 시스템에서 실행
        """
        # 입력 데이터 검증
        if order_type not in ["buy", "sell"]:
            logger.error(f"잘못된 주문 유형: {order_type}")
            return {"status": "failed", "reason": "Invalid order type"}
        
        if not isinstance(symbol, str) or not symbol.isalnum():
            logger.error(f"잘못된 심볼: {symbol}")
            return {"status": "failed", "reason": "Invalid symbol"}
        
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            logger.error(f"잘못된 수량: {quantity}")
            return {"status": "failed", "reason": "Invalid quantity"}
        
        try:
            # 거래 실행
            result = execute_trade(order_type, symbol, quantity)
            if result:
                logger.info(f"주문 성공: {order_type} {symbol} {quantity}")
                return {"status": "success"}
            else:
                logger.warning(f"주문 실패: {order_type} {symbol} {quantity}")
                return {"status": "failed", "reason": "Trade execution failed"}
        except Exception as e:
            logger.exception("거래 실행 중 예외 발생")
            return {"status": "failed", "reason": str(e)}
