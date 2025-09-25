import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from core.handlers import routers
from core.middlewares import DbSessionMiddleware
from infrastructure.database import init_db


async def main():
    load_dotenv()

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CONN_STRING_ASYNC = os.getenv("CONN_STRING_ASYNC")

    engine, session_maker = init_db(CONN_STRING_ASYNC)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

    for router in routers:
        dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    print("running")
    asyncio.run(main())
