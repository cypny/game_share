from aiogram import Router, F
from aiogram.types import CallbackQuery

from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(F.data == "no_action")
async def no_action(callback: CallbackQuery):
    await callback.answer()
