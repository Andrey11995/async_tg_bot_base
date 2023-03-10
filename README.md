# Async Telegram Bot
### Шаблон асинхронного бота на фреймворке Aiogram

Бот может общаться с базой данных PostgreSQL (с использованием ORM SQLAlchemy)
и сторонними API (например Notion) посредством отправки запросов через Aiohttp.

В основном бот использует webhooks, но для разработки добавлен polling
(переключается переменной WEBHOOK в .env файле).

В боте присутствуют обработчики отправленных текстовых файлов и таблиц Excel.

## Наполнение .env файла:
- WEBHOOK - 1 - webhook, 0 - polling
- WEBHOOK_HOST - домен сервера (обязательно с https)
- WEBHOOK_PREFIX - префикс перед токеном бота в url
- PORT - порт, на котором крутится бот
- TG_BOT_TOKEN - токен бота

Чтобы подключить БД (на примере PostgreSQL)
- POSTGRES_USER - имя пользователя БД
- POSTGRES_DB - название БД
- POSTGRES_PASSWORD - пароль пользователя БД
- POSTGRES_HOST - хост, где находится БД (имя docker контейнера с БД)

## Деплой:
1. На сервере устанавливаем git, docker и docker-compose;
2. Клонируем репозиторий и переходим в него;
3. Создаем .env файл в корне;
4. Запускаем: docker-compose up -d --build.

## Обновление:
1. Обновляем локальный репозиторий: git pull;
2. Опускаем контейнеры: docker-compose down;
3. Поднимаем контейнеры: docker-compose up -d --build.

## Технологии:
- Python 3.9
- Aiogram
- Aiohttp (для возможности делать запросы)
- SQLAlchemy (PostgreSQL)

- Docker
- Nginx (можно использовать локальный nginx без докера)
