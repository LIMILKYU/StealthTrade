import telebot
import subprocess
from config import Config

bot = telebot.TeleBot(Config.TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=["update"])
def update_code(message):
    """GitHub에서 최신 코드 업데이트"""
    output = subprocess.run(["git", "pull"], capture_output=True, text=True)
    bot.send_message(Config.TELEGRAM_CHAT_ID, f"📌 코드 업데이트 결과:\n{output.stdout}")

@bot.message_handler(commands=["restart"])
def restart_bot(message):
    """자동매매 봇 재시작"""
    try:
        # 실행 중인 run_bot.py 종료
        subprocess.run(["pkill", "-f", "run_bot.py"])
        
        # 새로운 프로세스로 run_bot.py 실행
        subprocess.Popen(["python3", "run_bot.py"])
        
        bot.send_message(Config.TELEGRAM_CHAT_ID, "🔄 자동매매 봇 재시작 완료!")
    except Exception as e:
        bot.send_message(Config.TELEGRAM_CHAT_ID, f"❌ 봇 재시작 실패: {str(e)}")

bot.polling()
