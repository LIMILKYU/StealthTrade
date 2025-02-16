# 트레이딩 성과(승률, MDD, ROI 등)를 요약하여 리포트 생성
# 리포트를 CSV 또는 PDF 파일로 저장 가능

import pandas as pd
import logging
from ai_optimization.performance_analysis import PerformanceAnalysis

class TradingReport:
    def __init__(self, trade_log_file: str):
        self.performance_analyzer = PerformanceAnalysis(trade_log_file)
        self.trade_log_file = trade_log_file
        logging.basicConfig(level=logging.INFO)

    def generate_report(self):
        """ 트레이딩 성과 리포트 생성 """
        performance = self.performance_analyzer.analyze_performance()
        report = f"""
        📊 **AI 트레이딩 성과 리포트**
        ----------------------------------------
        ✅ 승률: {performance["win_rate"]:.2f}%
        ✅ 최대 손실 (MDD): {performance["max_drawdown"]:.2f}
        ✅ 평균 손익비: {performance["risk_reward_ratio"]:.2f}
        ✅ 샤프비율: {performance["sharpe_ratio"]:.2f}
        """

        # 리포트를 CSV 파일로 저장
        report_df = pd.DataFrame([performance])
        report_df.to_csv("reports/daily_trading_report.csv", index=False)

        logging.info(f"📄 트레이딩 리포트 저장 완료: reports/daily_trading_report.csv")
        return report

# 사용 예시
if __name__ == "__main__":
    report_generator = TradingReport("data/trade_log.csv")
    print(report_generator.generate_report())
