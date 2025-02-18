import telegram
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 텔레그램 봇 설정
TRADE_ALERT_BOT = telegram.Bot(token=os.getenv("TELEGRAM_BOT_TRADE")) # 매매 신호 봇
MARKET_ANALYSIS_BOT = telegram.Bot(token=os.getenv("TELEGRAM_BOT_MARKET")) # 시장 분석 봇
SYSTEM_MONITOR_BOT = telegram.Bot(token=os.getenv("TELEGRAM_BOT_SYSTEM")) # 시스템 모니터링 봇
RISK_MANAGEMENT_BOT = telegram.Bot(token=os.getenv("TELEGRAM_BOT_RISK")) # 위험 관리 봇
TRADE_CONTROL_BOT = telegram.Bot(token=os.getenv("TELEGRAM_BOT_CONTROL")) # 트레이딩 컨트롤 봇
EDIT_BOT_TOKEN = os.getenv("TELEGRAM_BOT_EDIT")

# 매매 신호 봇 (매매 신호 및 주문 알림 전용)
def send_trade_alert(message):
    TRADE_ALERT_BOT.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=message)

# 시장 분석 봇 (시장 상황 및 AI 기반 분석 데이터 전송)
def send_market_analysis(message):
    MARKET_ANALYSIS_BOT.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=message)

# 시스템 모니터링 봇 (자동매매 시스템 상태 체크 및 오류 감지)
def send_system_alert(message):
    SYSTEM_MONITOR_BOT.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=message)

# 위험 관리 봇 (손실 감지, 연속 손실 발생 시 트레이딩 중단 경고)
def send_risk_alert(message):
    RISK_MANAGEMENT_BOT.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=message)

# 트레이딩 컨트롤 봇 (원격으로 자동매매 제어)
def control_trading(action):
    if action == "pause":
        send_system_alert("🚨 자동매매 시스템이 사용자에 의해 일시 중단되었습니다.")
        # 자동매매 중단 로직 추가
    elif action == "resume":
        send_system_alert("✅ 자동매매 시스템이 다시 시작되었습니다.")
        # 자동매매 재개 로직 추가
    elif action == "shutdown":
        send_system_alert("⚠️ 자동매매 시스템이 종료됩니다.")
        # 시스템 종료 로직 추가

def start(update, context):
    update.message.reply_text("🛠 코드 수정 요청 봇입니다. '[수정 요청] 파일명' 형식으로 요청해주세요.")

def process_edit_request(update, context):
    """ 사용자가 텔레그램을 통해 코드 수정 요청을 보내면 GitHub에 Issue 생성 """
    message = update.message.text
    if "[수정 요청]" not in message:
        update.message.reply_text("⚠️ '[수정 요청] 파일명' 형식으로 요청해 주세요.")
        return

    # 파일명과 요청 메시지 추출
    try:
        lines = message.split("\\n")
        title_line = lines[0].replace("[수정 요청]", "").strip()
        description = "\\n".join(lines[1:]).strip()
    except Exception:
        update.message.reply_text("⚠️ 형식 오류! 예제: '[수정 요청] trading_api.py\\n슬리피지 방어 기능 추가 요청'")
        return

    # GitHub Issue 생성
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {
        "title": title_line,
        "body": description,
        "labels": ["edit-request"]
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        issue_url = response.json().get("html_url")
        update.message.reply_text(f"✅ 코드 수정 요청이 접수되었습니다!\\nGitHub Issue: {issue_url}")
    else:
        update.message.reply_text("❌ GitHub Issue 생성 실패. 관리자에게 문의하세요.")

# 코드 수정 요청 봇
def main():
    updater = Updater(EDIT_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, process_edit_request))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    send_trade_alert("🚀 매매 신호 봇 테스트 메시지")
    send_market_analysis("📊 시장 분석 봇 테스트 메시지")
    send_system_alert("🛠 시스템 모니터링 봇 테스트 메시지")
    send_risk_alert("⚠️ 위험 관리 봇 테스트 메시지")

# 텔레그램 코드 수정 요청 봇 파일 생성
os.makedirs(os.path.dirname(telegram_edit_bot_path), exist_ok=True)
with open(telegram_edit_bot_path, "w", encoding="utf-8") as file:
    file.write(telegram_edit_bot_code)

# 생성된 파일 경로 반환
telegram_edit_bot_path