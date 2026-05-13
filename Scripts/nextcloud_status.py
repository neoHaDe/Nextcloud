import requests
import json
from datetime import datetime
import os
import sys
import tempfile

# вывод для бота
RESULT_FILE = os.path.join(tempfile.gettempdir(), "nextcloud_status_result.json")

LOG_FILE = r"F:\Scripts\status_log.txt"
NEXTCLOUD_STATUS_URL = "https://nas.nehade.xyz/status.php"

# Создаём папку для лога, если её нет
dir_name = os.path.dirname(LOG_FILE)
if dir_name:
    try:
        os.makedirs(dir_name, exist_ok=True)
    except OSError as e:
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump({"success": False, "message": f"Не удалось создать папку для логов: {e}"}, f)
        sys.exit(1)

result = {"success": False, "version": "неизвестна", "message": ""}

try:
    response = requests.get(NEXTCLOUD_STATUS_URL, timeout=10)
    response.raise_for_status()

    try:
        data = response.json()
    except ValueError:
        result["message"] = "Сервер вернул не JSON."
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f)
        sys.exit(1)

    version = data.get("version", "неизвестна")
    installed = data.get("installed", False)
    maintenance = data.get("maintenance", True)

    if installed and not maintenance:
        result["success"] = True
        result["version"] = version
        result["message"] = f"Nextcloud работает, версия {version}"
    else:
        result["message"] = "Сервер на обслуживании или не установлен!"

    # лог для людишек
    log_entry = (f"[{datetime.now()}] Nextcloud v{version} — "
                 f"installed: {installed}, maintenance: {maintenance}\n")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
    except IOError:
        pass  # Тихо, не спеша пропускаем, чтобы не сломать основной поток

except requests.exceptions.RequestException as e:
    result["message"] = f"Сетевая ошибка: {e}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"[{datetime.now()}] ОШИБКА: {e}\n")
    except IOError:
        pass

# Записываем итоговый результат в JSON
with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f)