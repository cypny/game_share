DOCKER_COMPOSE := docker compose
DOCKER_COMPOSE_RUN := $(DOCKER_COMPOSE) run --rm
DOCKER_RUN_BOT := $(DOCKER_COMPOSE_RUN) bot


# Запуск контейнеров
up:
	$(DOCKER_COMPOSE) up

# Пересобирает контейнеры, очищает бд, удаляет текущие миграции, создает новую и применяет ее
reset:
	${DOCKER_COMPOSE} down -v
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
up-d:
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

# Запуск бота (перед запуском применяется миграция)
start_bot:
	alembic upgrade head
	python -m game_share_bot

