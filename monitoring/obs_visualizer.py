# OBS(Open Broadcaster Software)와 연동하여 실시간 트레이딩 성과 및 매매 신호 방송 가능
# 트레이딩 성과 데이터를 실시간으로 업데이트하고 OBS에 출력

import logging
import time
from ai_optimization.performance_visualization import PerformanceVisualization

class OBSVisualizer:
    def __init__(self, trade_log_file: str):
        self.visualizer = PerformanceVisualization(trade_log_file)
        logging.basicConfig(level=logging.INFO)

    def update_obs(self):
        """ OBS 화면에 실시간 트레이딩 성과 출력 """
        while True:
            logging.info("🔄 Updating OBS with latest trading performance...")
            self.visualizer.plot_performance()
            time.sleep(30)  # 30초마다 업데이트

# 사용 예시
if __name__ == "__main__":
    obs_visualizer = OBSVisualizer("data/trade_log.csv")
    obs_visualizer.update_obs()
