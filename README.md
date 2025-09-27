# Game Share Bot

Telegram-бот для доступа к библиотеке консольных игр с системой платной подписки, написанный на Python 3.12 с использованием aiogram 

## Особенности

- Python 3.13
- Poetry для управления зависимостями
- aiogram 3.x для работы с Telegram API
- PosgreSQL для хранения данных
- Redis для хранения состояния
- Docker и docker-compose для контейнеризации
- YooKassa - формирование и обработка платежей
- Асинхронная обработка сообщений

### Установка

1. Установите зависимости:
```bash
poetry install
```

2. Создайте файл .env на основе .env.example:
```bash
cp .env.example .env
```

3. Отредактируйте .env файл, добавив необходимые значения   

   (В CONN_STRING_SYNC и CONN_STRING_ASYNC вместо user и password укажите свои данные для подключения к PostgreSQL)

4. Создайте БД под пользователем, которого указали в CONN_STRING_SYNC и CONN_STRING_ASYNC (подставьте в команду вместо user)
```bash
createdb -U user gameshare
```

5. Примените миграции, чтобы создать необходимые таблицы в базе данных:
```bash
poetry run alembic upgrade head
```

### Запуск

```bash
poetry run python -m game_share_bot
```

### Разработка

Если нужно добавить новую зависимость:
```bash
poetry add package_name
```

Если нужно добавить новую dev-зависимость (pytest и подобное), ее лучше добавлять отдельной командой:
```bash
poetry add --dev package_name
```

Если нужно удалить зависимость:
```bash
poetry remove package_name
```

Eсли меняете models - создавайте новую миграцию:
```bash
poetry run alembic revision --autogenerate -m "описание"
```

Она создаст файл .py в папке alembic/versions (его надо бы закоммитить)  
После чего примените миграцию (остальные тоже будут должны ее применить у себя):  
```bash
poetry run alembic upgrade head
```