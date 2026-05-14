import docker
import json
import os
import sys
from datetime import datetime

REPORT_FILE = r"F:\Scripts\container_report.json"
PREVIOUS_STATE_FILE = r"F:\Scripts\previous_containers.json"

def get_container_status():
    try:
        client = docker.from_env()
    except docker.errors.DockerException as e:
        return {"error": f"Не удалось подключиться к Docker: {e}"}

    containers_info = []
    for container in client.containers.list(all=True):
        try:
            container.reload()
        except docker.errors.NotFound:
            continue

        info = {
            "name": container.name,
            "status": container.status,
            "exit_code": container.attrs["State"].get("ExitCode", "") if container.status != "running" else "",
        }
        containers_info.append(info)

    return {"timestamp": datetime.now().isoformat(), "containers": containers_info}

def check_and_alert():
    current = get_container_status()
    if "error" in current:
        return {"error": current["error"]}

    prev = {}
    if os.path.exists(PREVIOUS_STATE_FILE):
        try:
            with open(PREVIOUS_STATE_FILE, 'r', encoding='utf-8') as f:
                prev = json.load(f)
        except:
            pass

    prev_map = {c['name']: c for c in prev.get('containers', [])}
    alerts = []

    for c in current['containers']:
        name = c['name']
        if name in prev_map:
            if prev_map[name]['status'] == 'running' and c['status'] != 'running':
                alerts.append({
                    'name': name,
                    'previous_status': 'running',
                    'current_status': c['status'],
                    'exit_code': c.get('exit_code', '')
                })

    #сохранение состояния 
    with open(PREVIOUS_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(current, f, ensure_ascii=False, indent=2)

    return {"alerts": alerts}

def generate_report():
    dir_name = os.path.dirname(REPORT_FILE)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    data = get_container_status()
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Отчёт сохранён в {REPORT_FILE}")

if __name__ == "__main__":
    if '--alert' in sys.argv:
        result = check_and_alert()
        print(json.dumps(result, ensure_ascii=False))
    else:
        generate_report()