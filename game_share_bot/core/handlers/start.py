from aiogram import Router, types
from aiogram.filters import CommandStart

from game_share_bot.core.keyboards.inline import main_menu_kb
from game_share_bot.core.logging import get_logger

router = Router()
logger = get_logger(__name__)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    logger.info(f"Команда /start от пользователя {user_id} (@{username})")

    await message.answer("/start command", reply_markup=main_menu_kb())
    logger.debug(f"Стартовое сообщение отправлено пользователю {user_id}")
