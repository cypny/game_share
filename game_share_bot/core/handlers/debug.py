from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.logging import get_logger

router = Router()
logger = get_logger(__name__)


@router.message(Command("debug"))
async def cmd_check_db(message: types.Message, session: AsyncSession):
    logger.info(f"Пользователь {message.from_user.id} выполнил команду debug")

    try:
        _ = await session.execute(text("SELECT 1"))
        logger.info("Подключение к базе данных успешно")
        await message.answer("✅ Подключение к БД успешно!")
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {str(e)}", exc_info=True)
        await message.answer(f"❌ Ошибка подключения к БД: {str(e)}")


@router.message(Command("admin"), IsAdmin())
async def cmd_check_admin(message: types.Message):
    await message.answer("Ты админ!!!!")


@router.message(Command("admin"))
async def cmd_check_admin(message: types.Message):
    await message.answer("Ты не админ(((")
