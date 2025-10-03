# Game Share Bot

Telegram-бот для доступа к библиотеке консольных игр с системой платной подписки, написанный на Python 3.12 с использованием aiogram 

## Особенности

- Асинхронная обработка сообщений
- PosgreSQL для хранения данных
- Redis для хранения состояния
- Docker для контейнеризации
- YooKassa для формирования и обработки платежей

### Подготовка

1. Создайте файл .env на основе .env.example:
```bash
cp .env.example .env
```

2. Отредактируйте .env файл, добавив токен бота

### Запуск

```bash
docker compose up -d
```

### Остановка приложения
```bash
docker compose down
```

### Разработка

Установка зависимостей:
```bash
poetry install
```

Запуск вне контейнера:
```bash
poetry run python -m game_share_bot
```

Пересобрать контейнер:
```bash
docker compose build
```

Eсли меняете models - создавайте новую миграцию:
```bash
poetry run alembic revision --autogenerate -m "описание"
```

Она создаст файл .py в папке alembic/versions (его надо бы закоммитить)

Применить миграции:
```bash
poetry run alembic upgrade head
```

Создать БД gameshare под пользователем user
```bash
createdb -U user gameshare
```