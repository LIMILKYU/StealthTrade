from fastapi import FastAPI
from trpc.server import TRPCServer
from backend.trading_api import TradingAPI
from backend.strategy_api import StrategyAPI
from backend.performance_api import PerformanceAPI

app = FastAPI()
trpc = TRPCServer()

# API 엔드포인트 등록
trpc.add_router("trading", TradingAPI)
trpc.add_router("strategy", StrategyAPI)
trpc.add_router("performance", PerformanceAPI)

@app.get("/")
async def health_check():
    return {"status": "tRPC Server Running"}

# tRPC 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
