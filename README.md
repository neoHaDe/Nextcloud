# 🏠 Домашний Дата-Центр

**Личное облако, мессенджер и система мониторинга в контейнерах Docker с AI-ассистентом.**

[![Tech Stack](https://skillicons.dev/icons?i=linux,docker,nginx,prometheus,grafana,git,github,python)](https://skillicons.dev)

## 🎯 О проекте

Полностью* (почти) автономная инфраструктура для личного облака, развернутая на **Windows 11** с использованием **Docker и Docker Compose**.

Проект создан для личного пользованя + как тренировка навыков и нарабатывания опыта. 

> Проект выполнен самостоятельно, с использованием AI-ассистента для ускорения написания конфигураций и скриптов, а также для изучения основ по принципу реверс-инжиниринга.

---

## 🧱 Архитектура

Все сервисы управляются **единым `docker-compose.yml`** и разделены на две изолированные Docker-сети:

- **nextcloud-net** — Nextcloud, MariaDB, Nginx Proxy Manager, Cron
- **monitor-net** — Prometheus, Grafana, cAdvisor, Node Exporter, Process Exporter

Nginx Proxy Manager подключён к обеим сетям и является единственной точкой входа снаружи.

```
Интернет (80/443)
      │
      ▼
Nginx Proxy Manager ──────────────────────────┐
      │                                        │
      │ nextcloud-net                          │ monitor-net
      ▼                                        ▼
  Nextcloud ◄── Cron                       Grafana
      │                                        ▲
      ▼                                        │
   MariaDB                               Prometheus
                                          ▲  ▲  ▲
                                   Node  cAdvisor  Process
                                 Exporter          Exporter
```

---

## 🛠 Технологический стек

| Категория | Инструменты |
|---|---|
| 🐳 Контейнеры | Docker, Docker Compose, Docker Volumes |
| 🌐 Веб-сервер | Nginx Proxy Manager, Let's Encrypt |
| 📊 Мониторинг | Prometheus, Grafana, cAdvisor, Node Exporter, Process Exporter, Windows Exporter |
| 💾 Базы данных | MariaDB |
| 🐍 Автоматизация | Python, python-telegram-bot, openai SDK |
| 🤖 AI | GitHub Models (GPT-4o-mini) |
| 🔗 Интеграции | Nextcloud API, Telegram Bot API, Docker SDK |
| 🧰 Прочее | Git, GitHub, PowerShell, WSL2 |

---

## 🤖 Telegram-бот с AI-ассистентом

Бот мониторит инфраструктуру в реальном времени и использует **GitHub Models (GPT-4o-mini)** для автоматической диагностики проблем.

### Команды

| Команда | Описание |
|---|---|
| `/start` | Подписаться на автоматические уведомления о падениях контейнеров |
| `/status` | Текущий статус Nextcloud (версия, режим обслуживания) |
| `/run_status` | Принудительная проверка Nextcloud с получением отчёта |
| `/containers` | Список всех Docker-контейнеров и их статусы |
| `/ask <вопрос>` | Задать произвольный вопрос AI-ассистенту по DevOps |

### Принцип работы

**Мониторинг контейнеров** (`container_monitor.py`) — каждые 30 секунд сравнивает текущее состояние контейнеров с предыдущим снимком. При обнаружении падения автоматически отправляет уведомление и запрашивает у AI объяснение и рекомендации.

**Проверка Nextcloud** (`nextcloud_status.py`) — обращается к `/status.php` и возвращает версию, статус установки и режим обслуживания.

**AI-ассистент** — доступен в автоматическом режиме (анализ падений) и вручную через `/ask`.

---

## 🔒 Безопасность

- Nextcloud доступен **только по HTTPS** через NPM — прямой порт наружу не открыт
- Внешнее хранилище `/mnt/nas` смонтировано с правами `770`, владелец `www-data` (UID 33)
- Все секреты хранятся в `.env`, который добавлен в `.gitignore`
- Версии всех образов зафиксированы — случайное обновление не сломает стек
- Две изолированные Docker-сети: мониторинг не имеет доступа к данным Nextcloud
- Конфиги Prometheus и Process Exporter встроены в `docker-compose.yml` — не нужны отдельные файлы на диске

---

## 📸 Скриншоты

![Grafana Dashboard](screenshots/grafana_dashboard.png)
*Дашборд Grafana с метриками хоста и контейнеров*

![Nextcloud Files](screenshots/nextcloud_files.png)
*Веб-интерфейс Nextcloud с подключённым внешним хранилищем*

![Nextcloud Talk](screenshots/nextcloud_talk.png)
*Видеозвонок через Nextcloud Talk (High Performance Backend)*

---

# 🚀 Быстрый старт

## 📋 Требования

- Windows 10/11 с WSL2 и Docker Desktop
- Статический IP и домен (например, `nextcloud.xyz`)
- Проброшены порты **80**, **443**, **3478 (TCP/UDP)** на роутере
- Свободное место: ~20 ГБ

---

## 1. Клонируем репозиторий

```bash
git clone https://github.com/neoHaDe/Nextcloud.git
cd Nextcloud
```

---

## 2. Проверяем структуру

```
Nextcloud/
├── docker-compose.yml        # весь стек + встроенные конфиги Prometheus и Process Exporter
├── Dockerfile                # образ Nextcloud с nas-init.sh
├── nas-init.sh               # выставляет права на /mnt/nas при старте
├── .env.example              # шаблон — скопировать в .env
├── monitoring/
│   └── grafana/
│       ├── dashboards/       # провижининг дашбордов Grafana
│       └── datasources/      # провижининг источника данных Grafana
├── Scripts/
│   ├── container_monitor.py  # мониторинг контейнеров
│   ├── nextcloud_status.py   # проверка Nextcloud
│   └── requirements.txt
└── Bots/
    └── nextcloud_bot.py      # Telegram-бот с AI
```

> Конфиги Prometheus и Process Exporter встроены прямо в `docker-compose.yml` —
> отдельные файлы `prometheus.yml` и `process-exporter-config.yml` для запуска не нужны.

---

## 3. Создаём `.env`

```bash
cp .env.example .env
```

Заполни все значения в `.env`:

```ini
# MariaDB
MYSQL_ROOT_PASSWORD=надёжный_пароль_root
MYSQL_PASSWORD=пароль_пользователя_nextcloud

# Grafana
GRAFANA_PASSWORD=пароль_grafana

# Telegram-бот
BOT_TOKEN=токен_от_BotFather

# AI-ассистент (GitHub Models)
# Получить: https://github.com/settings/tokens → Generate new token
GITHUB_TOKEN=твой_github_personal_access_token

# Talk HPB (только при запуске с --profile talk)
TURN_SECRET=
SIGNALING_SECRET=
INTERNAL_SECRET=
```

---

## 4. Настройка путей к данным

В `docker-compose.yml` замени пути у сервисов `nextcloud` и `nextcloud-cron`:

```yaml
volumes:
  - F:/NextcloudData:/var/www/html/data   # ← путь к папке с файлами пользователей
  - F:/SharedNAS:/mnt/nas                 # ← путь к общей папке
```

Часть после `:` — путь внутри контейнера, не трогай.

---

## 5. Запуск

### Первый запуск:

```bash
docker compose build
docker compose up -d
```

### Последующие запуски:

```bash
docker compose up -d
```

### С Nextcloud Talk HPB:

```bash
docker compose --profile talk up -d
```

Проверяем что все контейнеры поднялись:

```bash
docker compose ps
```

Первый запуск занимает 2–5 минут: MariaDB инициализирует базу, затем Nextcloud
дожидается её готовности. Nginx Proxy Manager в это время вернёт 502 — это нормально.

---

## 6. Настройка Nginx Proxy Manager

1. Открой `http://твой_IP:81`
2. Первый вход: `admin@example.com` / `changeme` — сразу смени
3. **Proxy Hosts → Add Proxy Host:**

| Поле | Nextcloud | Grafana |
|---|---|---|
| Domain Names | `nas.твой-домен.xyz` | `monitor.твой-домен.xyz` |
| Forward Hostname | `nextcloud_app` | `grafana` |
| Forward Port | `80` | `3000` |
| Websockets Support | ✅ | — |

4. Вкладка **SSL** → выпусти сертификат Let's Encrypt для каждого хоста

---

## 7. Первоначальная настройка Nextcloud

Открой `https://nas.твой-домен.xyz` и создай учётную запись администратора.
Nextcloud автоматически подключится к MariaDB.

---

## 8. Запуск Telegram-бота

```bash
cd Scripts
pip install -r requirements.txt
cd ../Bots
python nextcloud_bot.py
```

Отправь боту `/start` чтобы подписаться на уведомления.
Используй `/ask <вопрос>` для обращения к AI-ассистенту.

---

## 9. Проверка работоспособности

| Сервис | Адрес | Доступ |
|---|---|---|
| Nextcloud | `https://nas.твой-домен.xyz` | Создаётся при установке |
| Nginx Proxy Manager | `http://твой_IP:81` | Создаётся при первом входе |
| Grafana | `https://monitor.твой-домен.xyz` | `admin` / `GRAFANA_PASSWORD` |
| Prometheus | `http://localhost:9090` | Без аутентификации |
| Telegram-бот | `/status` в чате с ботом | — |

---

## 📈 Результаты

- ✅ Единый `docker-compose.yml` — весь стек одной командой
- ✅ Автоматическое восстановление контейнеров (`restart: always`)
- ✅ Nextcloud стартует только после готовности БД (`condition: service_healthy`)
- ✅ Cron в отдельном контейнере — независим от основного сервиса
- ✅ Мониторинг хоста и контейнеров: CPU, RAM, диск, сеть, процессы, Windows-метрики
- ✅ AI автоматически диагностирует падения и отвечает на вопросы
- ✅ Все секреты в `.env`, образы зафиксированы на версиях
- ✅ Две изолированные сети, Nextcloud без открытых портов наружу
- ✅ Конфиги встроены в compose — совместимо с Windows/WSL2 Docker Desktop

---

## 📁 Связанные репозитории

- **[ansible-playbooks](https://github.com/neoHaDe/ansible-playbooks)** — плейбуки для настройки серверов (в процессе)

## 📫 Контакты

- ✉️ [Email](mailto:nehadebackup@gmail.com)
- 📬 [Telegram](https://t.me/neHade)
