from trpc.server import TRPCRouter
from monitoring.real_time_monitor import get_performance_metrics

class PerformanceAPI(TRPCRouter):
    async def get_performance(self):
        """
        실시간 트레이딩 성과 분석 제공
        """
        metrics = get_performance_metrics()
        return metrics
