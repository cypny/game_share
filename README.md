# Game Share Bot

Telegram-бот для доступа к библиотеке консольных игр с системой платной подписки, написанный на Python 3.13 с использованием aiogram 

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

3. Для создания таблиц, запустите:
```bash
make reset
```

### Запуск

```bash
make up
```

### Остановка приложения
```bash
make down
```

### Разработка

Пересборка, очищение бд и все в таком духе:
```bash
make reset
```

#### Если вне контейнера:

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
make build
```

Создать новую миграцию:
```bash
poetry run alembic revision --autogenerate -m "описание"
```

Применить миграции:
```bash
poetry run alembic upgrade head
```

Создать БД gameshare под пользователем user
```bash
createdb -U user gameshare
```