from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.infrastructure.repositories import UserRepository
from game_share_bot.infrastructure.utils import get_logger

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

@router.message(Command("give_me_admin"))
async def cmd_give_me_admin(message: types.Message, session: AsyncSession):
    logger.warning(f"Запрос админа от пользователя {message.from_user.id}")
    try:
        user_repo = UserRepository(session)
        await user_repo.make_admin(message.from_user.id)
        logger.warning(f"Пользователь {message.from_user.id} назначен админом")
        await message.answer("Вы админ!")
    except Exception as e:
        logger.error(f"Не удалось назначить админа", exc_info=True)
        await message.answer("Не удалось назначить администратора")