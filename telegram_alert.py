import os
import requests
import logging
from dotenv import load_dotenv
from reporting.trading_report import TradingReport

# 환경 변수 로드
load_dotenv()

class TelegramNotifier:
    def __init__(self):
        """ 텔레그램 봇을 활용하여 트레이딩 성과 및 리포트 전송 """
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.report_generator = TradingReport("data/trade_log.csv")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        logging.basicConfig(level=logging.INFO)

    def send_message(self, message: str):
        """ 텔레그램 메시지 전송 """
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            response = requests.post(self.base_url, data=payload)
            if response.status_code == 200:
                logging.info("✅ 텔레그램 메시지 전송 성공")
            else:
                logging.error(f"❌ 텔레그램 메시지 전송 실패: {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"🚨 텔레그램 API 오류 발생: {e}")

    def send_trading_report(self):
        """ 트레이딩 성과 리포트를 텔레그램으로 전송 """
        try:
            report = self.report_generator.generate_report()
            if report:
                self.send_message(f"📊 **일일 트레이딩 성과 보고서**\n{report}")
            else:
                logging.warning("⚠️ 트레이딩 성과 보고서가 비어 있습니다.")
        except Exception as e:
            logging.error(f"🚨 트레이딩 리포트 생성 오류: {e}")

    def send_alert(self, alert_type: str, message: str):
        """ 특정 이벤트 발생 시 텔레그램 경고 메시지 전송 """
        alert_icons = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "🚨",
            "SUCCESS": "✅"
        }
        icon = alert_icons.get(alert_type.upper(), "🔔")
        self.send_message(f"{icon} *{alert_type}* - {message}")

# 사용 예시
if __name__ == "__main__":
    notifier = TelegramNotifier()
    notifier.send_message("✅ 텔레그램 알림 시스템이 정상적으로 동작합니다.")
    notifier.send_trading_report()
