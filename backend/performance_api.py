import logging
from typing import Dict, Any
from trpc.server import TRPCRouter
from monitoring.real_time_monitor import get_performance_metrics

# 로깅 설정
logger = logging.getLogger(__name__)

class PerformanceAPI(TRPCRouter):
    async def get_performance(self) -> Dict[str, Any]:
        """
        실시간 트레이딩 성과 분석 제공
        """
        try:
            metrics = get_performance_metrics()
            logger.info("성공적으로 성과 지표를 가져왔습니다.")
            return metrics
        except Exception as e:
            logger.error(f"성과 지표를 가져오는 중 오류 발생: {e}")
            return {"error": "성과 지표를 가져오는 중 오류가 발생했습니다."}
