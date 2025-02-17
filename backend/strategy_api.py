from trpc.server import TRPCRouter
from strategy.ai_strategy_optimizer import update_strategy

class StrategyAPI(TRPCRouter):
    async def optimize_strategy(self):
        """
        AI가 자동으로 전략을 최적화하고 업데이트
        """
        success = update_strategy()
        return {"status": "updated" if success else "failed"}
