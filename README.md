# 🏠 Домашний Дата-Центр

**Личное облако, мессенджер и система мониторинга в контейнерах Docker.**

[![Tech Stack](https://skillicons.dev/icons?i=linux,docker,nginx,prometheus,grafana,jenkins,git,github)](https://skillicons.dev)

## 🎯 О проекте

Полностью автономная инфраструктура (почти*) для личного облака, развернутая на **Windows 11** с использованием **Docker и Docker Compose**.  
Проект создан для демонстрации навыков контейнеризации, настройки обратного прокси, мониторинга, интеграции с внешними API и автоматизации с помощью Python.

P.S Проект выполнен самостоятельно, с использованием AI-ассистента для ускорения написания конфигураций и скриптов, а так же для изучения основ по принципу реверс-инжиниринга

## 🧱 Архитектура и взаимодействие сервисов

Все сервисы объединены в единую сеть Docker и управляются через `docker-compose.yml`:

- **Nextcloud** - центральное облачное хранилище, доступное по HTTPS через собственный домен.
- **Nextcloud Talk** - корпоративный мессенджер с аудио/видеозвонками (настроен High Performance Backend).
- **Nginx Proxy Manager** - обратный прокси-сервер с автоматическим выпуском SSL-сертификатов.
- **MariaDB** - база данных для Nextcloud.
- **Prometheus + Grafana + cAdvisor + Node Exporter** - система сбора и визуализации метрик.
- **Python-скрипты** - автоматическая проверка состояния Nextcloud с отправкой отчета в Telegram.

## 🛠 Технологический стек

| Категория       | Инструменты                                          |
|-----------------|------------------------------------------------------|
| 🐳 Контейнеры    | Docker, Docker Compose, Docker Volumes               |
| 🌐 Веб-сервер    | Nginx (прокси и реверс-прокси), Let's Encrypt                                                |
| 📊 Мониторинг    | Prometheus, Grafana, cAdvisor, Node Exporter                                                 |
| 💾 Базы данных   | MariaDB, SQLite                                                                              |
| 🐍 Скрипты       | Python (requests, python-telegram-bot, subprocess)                                           |
| 🔗 Интеграции    | Nextcloud API, Telegram Bot API, Gmail (IMAP/SMTP)                                           |
| ⚙️ Deployment    | Развертывание и управление жизненным циклом контейнеров на основе Docker Compose             |
| 🧰 Прочее        | Git, GitHub, PowerShell, WSL2                                                                |


## 🔒 Безопасность

- Внешнее хранилище `/mnt/nas` смонтировано с правами **`770`** и владельцем **`www-data`** (UID 33). Доступ к данным имеет только процесс Nextcloud.
- Доступ к Nextcloud и сопутствующим сервисам осуществляется **только по HTTPS** через Nginx Proxy Manager с автоматическим выпуском SSL-сертификатов.
- Все пароли, токены и секретные ключи вынесены в файл `.env`. В `docker-compose.yml` используются ссылки на переменные окружения (`${MYSQL_PASSWORD}` и т.д.).
- Для Python-скриптов конфиденциальные данные загружаются из переменных окружения с помощью библиотеки `python-dotenv`.
## 📸 Как это выглядит

![Grafana Dashboard](screenshots/grafana_dashboard.png)  
*Базовый дашбоард*

![Nextcloud Files](screenshots/nextcloud_files.png)  
*Веб-интерфейс Nextcloud с подключенным внешним диском (NAS) и почтовым клиентом.*

![Nextcloud Talk](screenshots/nextcloud_talk.png)  
*Видеозвонок через Nextcloud Talk с использованием High Performance Backend.*

## 📈 Ключевые результаты

- ✅ **Автоматическое восстановление** контейнеров после сбоев (`restart: always`).
- ✅ **Мониторинг 10+ ключевых хостовых метрик** в реальном времени.
- ✅ **Автоматическая проверка статуса** Nextcloud через Telegram-бота (ручной и периодический запуск).
- ✅ **Настроен HPB для Talk**, что позволяет проводить видеозвонки с 5+ участниками без задержек.
- ✅ **Интеграция с Gmail (IMAP/SMTP)** для почты, контактов и календарей.

## 📁 Связанные репозитории

- **[ansible-playbooks](https://github.com/neoHaDe/ansible-playbooks)** — плейбуки для настройки серверов (в процессе).

## 📫 Контакты

- ✉️ [Email](mailto:nehadebackup@gmail.com)
- 📬 [Telegram](https://t.me/neHade)  
