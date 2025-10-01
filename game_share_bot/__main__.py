import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from .core.handlers import routers
from .core.middlewares import DbSessionMiddleware
from .infrastructure.database import init_db
from .core.logging import setup_logging


async def main():
    # Настраиваем логирование
    setup_logging()
    logger = logging.getLogger(__name__)

    load_dotenv()

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CONN_STRING_ASYNC = os.getenv("CONN_STRING_ASYNC")

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения")
        return

    if not CONN_STRING_ASYNC:
        logger.error("CONN_STRING_ASYNC не найден в переменных окружения")
        return

    logger.info("Начало инициализации бота...")

    try:
        engine, session_maker = init_db(CONN_STRING_ASYNC)
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {str(e)}", exc_info=True)
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

    for router in routers:
        dp.include_router(router)
        logger.debug(f"Подключен роутер: {router.name}")

    logger.info("Бот успешно запущен")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Бот остановлен с ошибкой: {str(e)}", exc_info=True)
    finally:
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())