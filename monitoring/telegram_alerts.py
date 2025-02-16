# 📌 트레이딩 알림을 실시간으로 텔레그램으로 전송
# 매매 체결, 손절, 익절, 강제 청산 경고 발송
# API 장애 감지 시 알림 전송
# 텔레그램 봇을 사용하여 자동 메시지 전송

import requests
import logging

class TelegramAlerts:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        logging.basicConfig(level=logging.INFO)

    def send_alert(self, message: str):
        """ 텔레그램으로 알림 전송 """
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }
        response = requests.post(self.api_url, json=payload)
        if response.status_code == 200:
            logging.info(f"📢 Telegram Alert Sent: {message}")
        else:
            logging.warning(f"🚨 Telegram Alert Failed: {response.text}")

if __name__ == "__main__":
    bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"

    telegram = TelegramAlerts(bot_token, chat_id)
    telegram.send_alert("🚀 BTCUSDT 매수 체결 완료! 가격: $50,000")
