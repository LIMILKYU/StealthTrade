import telebot
import subprocess
from config import Config

bot = telebot.TeleBot(Config.TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=["update"])
def update_code(message):
    """GitHub에서 최신 코드 업데이트"""
    output = subprocess.run(["git", "pull"], capture_output=True, text=True)
    bot.send_message(Config.TELEGRAM_CHAT_ID, f"📌 코드 업데이트 결과:\n{output.stdout}")

bot.polling()
