# 📌 OBS를 활용하여 실시간 매매 정보를 시각화
# 진입 포지션, 손익(PnL), 시장 변동성 표시
# 트레이딩 차트를 실시간 스트리밍 가능

import logging
import json
import time
import os

class OBSVisualizer:
    def __init__(self, output_file="visualization/obs_data.json"):
        """
        OBS에서 읽을 JSON 파일을 생성하여 실시간 데이터 표시
        """
        self.output_file = output_file
        self.ensure_directory()
        logging.basicConfig(level=logging.INFO)

    def ensure_directory(self):
        """ visualization 폴더가 없으면 생성 """
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    def update_data(self, symbol: str, price: float, position: str, pnl: float):
        """ OBS JSON 파일 업데이트 """
        data = {
            "symbol": symbol,
            "price": price,
            "position": position,
            "pnl": pnl,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(self.output_file, "w") as f:
            json.dump(data, f, indent=4)
        logging.info(f"📊 OBS Data Updated: {data}")

# 사용 예시
if __name__ == "__main__":
    obs = OBSVisualizer()
    obs.update_data("BTCUSDT", 50000, "LONG", 150)  # 예제 데이터

