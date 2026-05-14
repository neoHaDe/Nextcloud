import os
import sys
import subprocess
import json
import tempfile
import openai
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue
from datetime import datetime
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

# Конфигурация клиента GitHub Models
github_client = openai.OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN")     
)

GITHUB_MODEL = "openai/gpt-4o-mini"            

def ask_ai(question: str) -> str:
    """Отправляет вопрос к GitHub Models и возвращает ответ."""
    try:
        response = github_client.chat.completions.create(
            model=GITHUB_MODEL,
            messages=[
                {"role": "system", "content": "Ты — ассистент DevOps-инженера. Отвечай кратко, по делу, помогай диагностировать и исправлять проблемы."},
                {"role": "user", "content": question},
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Ошибка при обращении к AI: {e})"

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
    """Загружает сохранённый ID чата из файла."""
    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, 'r') as f:
            return int(f.read().strip())
    return None

def run_script():
    """Запускает nextcloud_status.py и возвращает словарь с результатом."""
    subprocess.run(
        [sys.executable, SCRIPT_PATH],
        capture_output=True,
        timeout=30
    )
    if os.path.exists(RESULT_FILE):
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"success": False, "version": "неизвестна",
                "message": "Скрипт не выполнился (нет файла результата)."}

def get_report():
    """Формирует отчёт о состоянии Nextcloud для Telegram."""
    result = run_script()
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if result.get("success"):
        status = "✅"
    else:
        status = "❌"
    return f"🕒 {dt}\n{status} {result.get('message', '')}"

# ---------- Обработчики команд ----------
async def status_command(update, context: ContextTypes.DEFAULT_TYPE):
    report = get_report()
    await update.message.reply_text(report)

async def run_status_command(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Запускаю проверку...")
    report = get_report()
    await update.message.reply_text(report)

async def containers_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет сводку по всем Docker-контейнерам."""
    subprocess.run(
        [sys.executable, MONITOR_SCRIPT],
        capture_output=True,
        timeout=30
    )

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

    lines = [f"🕒 {data.get('timestamp', 'время неизвестно')}"]
    for c in data.get("containers", []):
        status_icon = "🟢" if c["status"] == "running" else "🔴"
        lines.append(f"{status_icon} {c['name']} ({c['status']})")

    await update.message.reply_text("\n".join(lines))

async def start_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Подписывает чат на уведомления о падениях контейнеров."""
    global NOTIFY_CHAT_ID
    NOTIFY_CHAT_ID = update.effective_chat.id
    with open(CHAT_ID_FILE, 'w') as f:
        f.write(str(NOTIFY_CHAT_ID))
    await update.message.reply_text("Вы подписаны на уведомления о падении контейнеров.")

async def check_containers_periodically(context: ContextTypes.DEFAULT_TYPE):
    """Периодическая проверка контейнеров и отправка уведомлений с AI-анализом."""
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
            exit_code = a.get('exit_code', '?')
            container_name = a['name']
            lines.append(f"🔴 {container_name} → {a['current_status']} (exit code {exit_code})")

            # Автоматический анализ через GitHub Models
            question = f"Контейнер {container_name} упал с кодом ошибки {exit_code}. Объясни, что это значит и как исправить."
            analysis = ask_ai(question)
            lines.append(f"🤖 AI: {analysis}")

        await context.bot.send_message(chat_id=NOTIFY_CHAT_ID, text="\n".join(lines))

async def ask_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Ручной запрос к AI."""
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text("Пожалуйста, напишите вопрос после /ask. Например: /ask Почему контейнер упал с кодом 137?")
        return

    await update.message.reply_text("⏳ AI анализирует...")
    answer = ask_ai(question)
    await update.message.reply_text(answer)

# ---------- Главная функция ----------
def main():
    application = Application.builder().token(BOT_TOKEN).job_queue(JobQueue()).build()
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("run_status", run_status_command))
    application.add_handler(CommandHandler("containers", containers_command))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ask", ask_command))

    # Запускаем проверку каждые 5 минут (300 секунд)
    job_queue = application.job_queue
    job_queue.run_repeating(check_containers_periodically, interval=30, first=10)

    print("Бот запущен. Ожидаю команды /status, /run_status, /containers, /start и /ask...")
    global NOTIFY_CHAT_ID
    NOTIFY_CHAT_ID = load_chat_id()
    application.run_polling()

if __name__ == "__main__":
    main()
