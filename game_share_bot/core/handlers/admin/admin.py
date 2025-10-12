from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.handlers.utils import respond_user
from game_share_bot.core.keyboards import admin_kb
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter(F.action == "return_to_main"), IsAdmin())  # type: ignore
@router.message(Command("admin"), IsAdmin())
async def admin_panel(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    text = "Вы администратор! Держите админ панель"
    markup = admin_kb()
    await respond_user(event, text, markup)


@router.message(Command("admin"))
async def admin_panel_for_non_admins(message: Message):
    await message.answer("У вас нет прав администратора(")
