import { TRPCRouter } from "@trpc/server";
import { getPerformanceMetrics } from "./performance_service";

export class PerformanceAPI extends TRPCRouter {
    async get_performance() {
        return getPerformanceMetrics();
    }
}
