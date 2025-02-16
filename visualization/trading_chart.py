# 실시간 트레이딩 차트 생성
# 가격 변동 & 포지션 변화를 차트로 시각화
# OBS에 연동할 이미지 파일 자동 업데이트

import matplotlib.pyplot as plt
import json
import os
import logging

class TradingChart:
    def __init__(self, json_file="visualization/obs_data.json", output_image="visualization/trading_chart.png"):
        """
        OBS에 연동할 실시간 차트 이미지 생성
        """
        self.json_file = json_file
        self.output_image = output_image
        self.ensure_directory()
        logging.basicConfig(level=logging.INFO)

    def ensure_directory(self):
        """ visualization 폴더가 없으면 생성 """
        os.makedirs(os.path.dirname(self.json_file), exist_ok=True)

    def load_data(self):
        """ JSON 데이터 로드 """
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("⚠ No valid data found, using default values.")
            return {"symbol": "BTCUSDT", "price": 0, "position": "NONE", "pnl": 0}

    def generate_chart(self):
        """ 실시간 트레이딩 차트 생성 """
        data = self.load_data()

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(["PnL"], [data["pnl"]], color="green" if data["pnl"] > 0 else "red")
        ax.set_title(f"{data['symbol']} Position: {data['position']}\nPrice: {data['price']} USDT")
        ax.set_xlabel("PnL (Profit & Loss)")
        plt.savefig(self.output_image, bbox_inches="tight")
        logging.info(f"📊 Trading Chart Updated: {self.output_image}")

# 사용 예시
if __name__ == "__main__":
    chart = TradingChart()
    chart.generate_chart()
