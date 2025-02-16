# 실시간 매매 상황 및 전략 변화를 모니터링
# 웹 대시보드 또는 OBS 화면을 통해 AI 전략 변화를 시각화

import time
import logging
from ai_optimization.ai_real_time_optimizer import AIRealTimeOptimizer

class RealTimeMonitor:
    def __init__(self, api_url: str, trade_log_file: str):
        self.ai_optimizer = AIRealTimeOptimizer(api_url, trade_log_file)
        logging.basicConfig(level=logging.INFO)

    def start_monitoring(self):
        """ 실시간 AI 트레이딩 성과 및 전략 모니터링 """
        logging.info("🚀 Real-Time AI Trading Monitor Started")
        while True:
            optimized_signal = self.ai_optimizer.update_strategy()
            logging.info(f"📊 AI Real-Time Optimized Signal: {optimized_signal}")
            time.sleep(5)  # 5초마다 업데이트

# 사용 예시
if __name__ == "__main__":
    monitor = RealTimeMonitor("https://api.binance.com/api/v3/ticker/24hr", "data/trade_log.csv")
    monitor.start_monitoring()
