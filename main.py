import logging
from fastapi import FastAPI
from trpc.server import TRPCServer
from backend.trading_api import TradingAPI
from backend.strategy_api import StrategyAPI
from backend.performance_api import PerformanceAPI

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 및 tRPC 서버 생성
app = FastAPI()
trpc = TRPCServer()

# tRPC 라우터 등록
trpc.add_router("trading", TradingAPI)
trpc.add_router("strategy", StrategyAPI)
trpc.add_router("performance", PerformanceAPI)

# FastAPI 애플리케이션에 tRPC 포함
app.include_router(trpc.router, prefix="/trpc")

# 헬스 체크 엔드포인트
@app.get("/")
async def health_check():
    logger.info("헬스 체크 엔드포인트 호출됨")
    return {"status": "✅ StealthTrader tRPC Server Running"}

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    logger.info("StealthTrader tRPC 서버 실행 중...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
