import os
import io
import sys
import subprocess
import json
import tempfile
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue
from datetime import datetime
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)


from telegram.ext import Application, CommandHandler, ContextTypes

# Мониторинг контейнеров
REPORT_FILE = r"F:\Scripts\container_report.json"
MONITOR_SCRIPT = r"F:\Scripts\container_monitor.py"
CHAT_ID_FILE = r"F:\Bots\chat_id.txt"
NOTIFY_CHAT_ID = None

BOT_TOKEN = os.getenv("BOT_TOKEN")
SCRIPT_PATH = r"F:\Scripts\nextcloud_status.py"
LOG_FILE = r"F:\Scripts\status_log.txt"
RESULT_FILE = os.path.join(tempfile.gettempdir(), "nextcloud_status_result.json")

def load_chat_id():
    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, 'r') as f:
            return int(f.read().strip())
    return None

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
    await update.message.reply_text("Запускаю проверку...")
    report = get_report()
    await update.message.reply_text(report)

async def containers_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /containers – присылает статус всех контейнеров."""
    # сам скрипт мониторинга
    subprocess.run(
        [sys.executable, MONITOR_SCRIPT],
        capture_output=True,
        timeout=30
    )

    # проверка отчёта
    if not os.path.exists(REPORT_FILE):
        await update.message.reply_text("Отчёт о контейнерах не найден. Проверьте работу скрипта.")
        return

    try:
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        await update.message.reply_text(f"Ошибка чтения отчёта: {e}")
        return

    if "error" in data:
        await update.message.reply_text(f"Ошибка: {data['error']}")
        return

    # результат
    lines = [f"🕒 {data.get('timestamp', 'время неизвестно')}"]
    for c in data.get("containers", []):
        status_icon = "🟢" if c["status"] == "running" else "🔴"
        name = c["name"]
        status = c["status"]
        lines.append(f"{status_icon} {name} ({status})")

    await update.message.reply_text("\n".join(lines))

async def start_command(update, context: ContextTypes.DEFAULT_TYPE):
    global NOTIFY_CHAT_ID
    NOTIFY_CHAT_ID = update.effective_chat.id
    with open(CHAT_ID_FILE, 'w') as f:
        f.write(str(NOTIFY_CHAT_ID))
    await update.message.reply_text("Вы подписаны на уведомления о падении контейнеров.")

async def check_containers_periodically(context: ContextTypes.DEFAULT_TYPE):
    global NOTIFY_CHAT_ID
    if NOTIFY_CHAT_ID is None:
        NOTIFY_CHAT_ID = load_chat_id()
    if NOTIFY_CHAT_ID is None:
        return

    result = subprocess.run(
        [sys.executable, MONITOR_SCRIPT, '--alert'],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode != 0:
        return

    try:
        data = json.loads(result.stdout)
    except:
        return

    if 'error' in data:
        return

    alerts = data.get('alerts', [])
    if alerts:
        lines = ["⚠️ Сбой контейнера(ов):"]
        for a in alerts:
            lines.append(f"🔴 {a['name']} → {a['current_status']} (exit code {a.get('exit_code', '?')})")
        await context.bot.send_message(chat_id=NOTIFY_CHAT_ID, text="\n".join(lines))

def main():
    application = Application.builder().token(BOT_TOKEN).job_queue(JobQueue()).build()
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("run_status", run_status_command))
    application.add_handler(CommandHandler("containers", containers_command))
    application.add_handler(CommandHandler("start", start_command))

    job_queue = application.job_queue
    job_queue.run_repeating(check_containers_periodically, interval=300, first=10)
    print("Бот запущен. Ожидаю команды /status и /run_status...")
    global NOTIFY_CHAT_ID
    NOTIFY_CHAT_ID = load_chat_id()
    application.run_polling()

if __name__ == "__main__":
    main()
