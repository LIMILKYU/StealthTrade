import requests

TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("✅ 텔레그램 알림 전송 완료!")
    else:
        print("❌ 텔레그램 알림 실패:", response.json())

if __name__ == "__main__":
    send_telegram_alert("📢 StealthTrader 자동매매 시스템 알림 테스트")
