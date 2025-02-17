from fastapi import FastAPI
from trpc.server import TRPCServer
from backend.trading_api import TradingAPI
from backend.strategy_api import StrategyAPI
from backend.performance_api import PerformanceAPI

# FastAPI 기반 tRPC 서버 생성
app = FastAPI()
trpc = TRPCServer()

# 📌 API 엔드포인트 등록
trpc.add_router("trading", TradingAPI)       # 매매 실행 API
trpc.add_router("strategy", StrategyAPI)     # AI 전략 최적화 API
trpc.add_router("performance", PerformanceAPI) # 트레이딩 성과 분석 API

@app.get("/")
async def health_check():
    return {"status": "✅ StealthTrader tRPC Server Running"}

# 📌 tRPC 서버 실행
if __name__ == "__main__":
    import uvicorn
    print("🚀 StealthTrader tRPC 서버 실행 중...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
