import { PerformanceAPI } from "@backend/performance_api";
import { initTRPC } from "@trpc/server";
import { StrategyAPI } from "./strategy_api";
import { TradingAPI } from "./trading_api";

const t = initTRPC.create();

export const appRouter = t.router({
    trading: t.procedure.query(() => TradingAPI),
    strategy: t.procedure.query(() => StrategyAPI),
    performance: t.procedure.query(() => PerformanceAPI),
});

export type AppRouter = typeof appRouter;
