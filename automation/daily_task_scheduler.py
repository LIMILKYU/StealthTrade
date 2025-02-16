# 매일 정해진 시간에 자동으로 트레이딩 리포트를 생성하고 텔레그램으로 전송
# Python schedule 라이브러리를 사용하여 자동 실행

import schedule
import time
import logging
from notification.telegram_notifier import TelegramNotifier

class DailyTaskScheduler:
    def __init__(self, bot_token: str, chat_id: str, trade_log_file: str):
        self.notifier = TelegramNotifier(bot_token, chat_id, trade_log_file)
        logging.basicConfig(level=logging.INFO)

    def schedule_tasks(self):
        """ 매일 트레이딩 리포트 자동 전송 """
        schedule.every().day.at("08:00").do(self.notifier.send_trading_report)  # 매일 오전 8시에 실행
        logging.info("✅ AI 트레이딩 리포트 자동 전송 스케줄링 완료")

    def run(self):
        """ 스케줄러 실행 """
        self.schedule_tasks()
        while True:
            schedule.run_pending()
            time.sleep(60)

# 사용 예시
if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
    TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
    scheduler = DailyTaskScheduler(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, "data/trade_log.csv")
    scheduler.run()
