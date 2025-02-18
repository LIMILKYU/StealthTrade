import telebot
import subprocess
import os
from config import Config

bot = telebot.TeleBot(Config.TELEGRAM_BOT_TOKEN)

# 저장된 파일 수정 대기열
edit_sessions = {}

@bot.message_handler(commands=["update"])
def update_code(message):
    """GitHub에서 최신 코드 업데이트"""
    output = subprocess.run(["git", "pull"], capture_output=True, text=True)
    bot.send_message(Config.TELEGRAM_CHAT_ID, f"📌 코드 업데이트 결과:\n{output.stdout}")

@bot.message_handler(commands=["restart"])
def restart_bot(message):
    """자동매매 봇 재시작"""
    try:
        subprocess.run(["pkill", "-f", "run_bot.py"])
        subprocess.Popen(["python3", "run_bot.py"])
        bot.send_message(Config.TELEGRAM_CHAT_ID, "🔄 자동매매 봇 재시작 완료!")
    except Exception as e:
        bot.send_message(Config.TELEGRAM_CHAT_ID, f"❌ 봇 재시작 실패: {str(e)}")

@bot.message_handler(commands=["edit"])
def edit_file(message):
    """파일 내용을 불러와 수정할 준비"""
    try:
        file_name = message.text.split(" ", 1)[1]
        if not os.path.exists(file_name):
            bot.send_message(Config.TELEGRAM_CHAT_ID, f"❌ 파일이 존재하지 않습니다: {file_name}")
            return
        
        with open(file_name, "r", encoding="utf-8") as f:
            file_content = f.read()
        
        bot.send_message(Config.TELEGRAM_CHAT_ID, f"📝 현재 파일 내용:\n```\n{file_content[:2000]}\n```", parse_mode="Markdown")
        bot.send_message(Config.TELEGRAM_CHAT_ID, "✍ 수정할 내용을 입력해주세요. '/save' 입력 시 저장됩니다.")

        edit_sessions[message.chat.id] = {"file_name": file_name, "content": ""}
    
    except Exception as e:
        bot.send_message(Config.TELEGRAM_CHAT_ID, f"❌ 오류 발생: {str(e)}")

@bot.message_handler(func=lambda message: message.chat.id in edit_sessions)
def receive_edit_content(message):
    """사용자가 수정할 내용을 입력받음"""
    chat_id = message.chat.id
    if message.text.strip() == "/save":
        session = edit_sessions.pop(chat_id)
        with open(session["file_name"], "w", encoding="utf-8") as f:
            f.write(session["content"])
        
        # GitHub에 자동 커밋
        subprocess.run(["git", "add", session["file_name"]])
        subprocess.run(["git", "commit", "-m", f"🔄 {session['file_name']} 수정"])
        subprocess.run(["git", "push"])

        bot.send_message(chat_id, f"✅ {session['file_name']} 수정 완료 & GitHub 반영됨!")
    else:
        edit_sessions[chat_id]["content"] += message.text + "\n"

bot.polling()
