import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import start, user, menu

async def main():
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(user.router)
    dp.include_router(menu.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    print("running")
    asyncio.run(main())
