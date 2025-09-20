from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import text

from infrastructure.database import SessionLocal

router = Router()


@router.message(Command("check"))
async def cmd_check_db(message: types.Message):
    try:
        async with SessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            await message.answer("✅ Подключение к БД успешно!")

    except Exception as e:
        await message.answer(f"❌ Ошибка подключения к БД: {str(e)}")
