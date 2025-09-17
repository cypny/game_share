import asyncio
import os
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message()
async def echo_handler(message: types.Message):
    await message.answer("я бот")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
