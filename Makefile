DOCKER_COMPOSE := docker compose
DOCKER_COMPOSE_RUN := $(DOCKER_COMPOSE) run --rm
DOCKER_RUN_BOT := $(DOCKER_COMPOSE_RUN) bot
PSQL := $(DOCKER_COMPOSE) exec -e PGPASSWORD=postgres db psql -U postgres -d gameshare

# Запуск контейнеров
up:
	$(DOCKER_COMPOSE) up

# Пересобирает контейнеры, очищает бд, удаляет текущие миграции, создает новую и применяет ее
reset:
	${DOCKER_COMPOSE} down -v
	$(MAKE) build
	$(MAKE) up-d
	$(MAKE) wait_db
	$(MAKE) drop_db
	$(MAKE) init_db
	$(DOCKER_RUN_BOT) rm -f app/alembic/versions/*.py
	$(MAKE) migration
	$(MAKE) migrate
	$(MAKE) down

# Проверяет, запущена ли бд; ждет запуска
wait_db:
	@echo "Waiting for DB to become healthy..."
	@until [ "$$(docker inspect --format='{{.State.Health.Status}}' $$(docker compose ps -q db))" = "healthy" ]; do \
		sleep 2; \
	done
	@echo "DB is healthy!"

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
	$(DOCKER_RUN_BOT) mkdir -p /app/alembic/versions
	$(DOCKER_RUN_BOT) alembic revision --autogenerate

# Применить миграцию (контейнеры должны быть запущены)
migrate:
	$(DOCKER_RUN_BOT) alembic upgrade head

# Удаление всех таблиц в бд (контейнеры должны быть запущены)
drop_db:
	$(PSQL) -f /app/sql/drop.sql

init_db:
	$(PSQL) -f /app/sql/init.sql

# Запуск бота (перед запуском применяется миграция)
start_bot:
	alembic upgrade head
	python -m game_share_bot

# Запуск тестов
test:
	poetry run pytest

