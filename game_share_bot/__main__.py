import asyncio
import os
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from message_controller import start_listening
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)






async def main():
    await start_listening(bot)


if __name__ == "__main__":
    asyncio.run(main())
