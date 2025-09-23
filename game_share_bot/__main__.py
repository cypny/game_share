import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import routers
from middlewares import DbSessionMiddleware
from infrastructure.database import session_maker


async def main():
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

    for router in routers:
        dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    print("running")
    asyncio.run(main())
