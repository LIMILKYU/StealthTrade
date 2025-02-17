import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# 🔹 텔레그램 메시지 전송 함수
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print("✅ 텔레그램 메시지 전송 성공!")
    else:
        print("❌ 텔레그램 메시지 전송 실패:", response.text)

# 🔹 테스트 메시지 보내기
if __name__ == "__main__":
    send_telegram_message("📢 StealthTrader 자동매매 시스템이 시작되었습니다!")
