import asyncio
import os

import redis.asyncio as redis
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from dotenv import load_dotenv

from game_share_bot.core.handlers import routers
from game_share_bot.core.middlewares import DbSessionMiddleware
from game_share_bot.domain.payment.yookassa_service import init_yookassa
from game_share_bot.infrastructure.database import init_db
from game_share_bot.infrastructure.utils import get_logger, setup_logging
from game_share_bot.scheduler.scheduler import get_scheduler

setup_logging()
logger = get_logger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST  = os.getenv("POSTGRES_HOST", "db")
CONN_STRING_ASYNC = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"


async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Перезапуск бота"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="menu", description="Главное меню"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения")
        return

    if not CONN_STRING_ASYNC:
        logger.error("CONN_STRING_ASYNC не найден в переменных окружения")
        return

    logger.info("Начало инициализации бота...")

    try:
        engine, session_maker = await init_db(CONN_STRING_ASYNC)
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {str(e)}", exc_info=True)
        return

    bot = Bot(token=BOT_TOKEN)

    redis_client = redis.Redis(host="redis", port=6379, db=0)
    storage = RedisStorage(redis_client)

    dp = Dispatcher(storage=storage)
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

    await set_default_commands(bot)

    for router in routers:
        dp.include_router(router)
        logger.debug(f"Подключен роутер: {router.name}")

    async def on_startup(dp: Dispatcher):
        scheduler = get_scheduler(bot, session_maker)
        scheduler.start()

    try:
        init_yookassa()
        await on_startup(dp)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Бот остановлен с ошибкой: {str(e)}", exc_info=True)
    finally:
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
