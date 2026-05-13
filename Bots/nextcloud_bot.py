import os
import sys
import subprocess
import json
import tempfile
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


from telegram.ext import Application, CommandHandler, ContextTypes


BOT_TOKEN = os.getenv("BOT_TOKEN")
SCRIPT_PATH = r"F:\Scripts\nextcloud_status.py"
LOG_FILE = r"F:\Scripts\status_log.txt"
RESULT_FILE = os.path.join(tempfile.gettempdir(), "nextcloud_status_result.json")


def run_script():
    """Запускает скрипт и возвращает словарь с результатом."""
    subprocess.run(
        [sys.executable, SCRIPT_PATH],
        capture_output=True,
        timeout=30
    )
    # результат скрипта в джейсоне
    if os.path.exists(RESULT_FILE):
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"success": False, "version": "неизвестна",
                "message": "Скрипт не выполнился (нет файла результата)."}

def get_report():
    result = run_script()
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if result.get("success"):
        status = "✅"
    else:
        status = "❌"
    return f"🕒 {dt}\n{status} {result.get('message', '')}"

async def status_command(update, context: ContextTypes.DEFAULT_TYPE):
    report = get_report()
    await update.message.reply_text(report)

async def run_status_command(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Запускаю проверку...")
    report = get_report()
    await update.message.reply_text(report)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("run_status", run_status_command))
    print("Бот запущен. Ожидаю команды /status и /run_status...")
    application.run_polling()

if __name__ == "__main__":
    main()
