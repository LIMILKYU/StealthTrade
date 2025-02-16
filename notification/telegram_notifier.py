# 텔레그램 봇을 활용하여 트레이딩 성과 및 리포트 전송
# 일일 트레이딩 성과를 요약하여 자동 전송

import requests
import logging
from reporting.trading_report import TradingReport

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str, trade_log_file: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.report_generator = TradingReport(trade_log_file)
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        logging.basicConfig(level=logging.INFO)

    def send_message(self, message: str):
        """ 텔레그램 메시지 전송 """
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"}
        response = requests.post(self.base_url, data=payload)
        if response.status_code == 200:
            logging.info("✅ 텔레그램 메시지 전송 성공")
        else:
            logging.error(f"❌ 텔레그램 메시지 전송 실패: {response.text}")

    def send_trading_report(self):
        """ 트레이딩 성과 리포트를 텔레그램으로 전송 """
        report = self.report_generator.generate_report()
        self.send_message(report)

# 사용 예시
if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
    TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
    notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, "data/trade_log.csv")
    notifier.send_trading_report()
