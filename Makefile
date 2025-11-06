DOCKER_COMPOSE := docker compose
DOCKER_COMPOSE_RUN := $(DOCKER_COMPOSE) run --rm
DOCKER_RUN_BOT := $(DOCKER_COMPOSE_RUN) bot


# Вот сюда тыкайте и все заработает (надеюсь)
# если не заработает - попробуйте перед этим сделать make reset
run:
	$(MAKE) up
	$(MAKE) migrate
	$(MAKE) start_bot

# Пересобирает контейнеры, очищает бд, удаляет текущие миграции, создает новую и применяет ее
reset:
	$(MAKE) build
	$(MAKE) up
	$(MAKE) drop_db
	rm -f alembic/versions/*.py
	$(MAKE) migration
	$(MAKE) migrate
	$(MAKE) down

# Сборка контейнеров
build:
	${DOCKER_COMPOSE} build

# Запуск контейнеров в фоне
up:
	$(DOCKER_COMPOSE) up -d

# Остановка контейнеров
down:
	$(DOCKER_COMPOSE) down

# Создать миграцию (контейнеры должны быть запущены)
migration:
	$(DOCKER_RUN_BOT) alembic revision --autogenerate

# Применить миграцию (контейнеры должны быть запущены)
migrate:
	$(DOCKER_RUN_BOT) alembic upgrade head

# Удаление всех таблиц в бд (контейнеры должны быть запущены)
drop_db:
	$(DOCKER_COMPOSE) exec -e PGPASSWORD=postgres db \
		psql -U postgres \
		-d gameshare \
		-f /app/sql/drop.sql

# Запуск бота (контейнеры должны быть запущены)
start_bot:
	$(DOCKER_RUN_BOT) python -m game_share_bot
