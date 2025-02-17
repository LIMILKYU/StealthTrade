from trpc.server import TRPCRouter
from execution.real_time_trading import execute_trade

class TradingAPI(TRPCRouter):
    async def place_order(self, order_type: str, symbol: str, quantity: float):
        """
        웹 대시보드에서 매매 요청을 받아 자동매매 시스템에서 실행
        """
        result = execute_trade(order_type, symbol, quantity)
        return {"status": "success" if result else "failed"}
