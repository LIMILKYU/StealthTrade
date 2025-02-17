import PerformanceChart from "../components/PerformanceChart";
import TradingPanel from "../components/TradingPanel";

export default function Home() {
    return (
        <div>
            <h1>📊 StealthTrader 대시보드</h1>
            <TradingPanel />
            <PerformanceChart />
        </div>
    );
}
