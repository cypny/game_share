from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.handlers.utils import respond_user
from game_share_bot.core.keyboards import admin_main_panel_kb
from game_share_bot.domain.enums import AdminAction
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter_by_action(AdminAction.RETURN_TO_MAIN_PANEL), IsAdmin())
@router.message(Command("admin"), IsAdmin())
async def admin_panel(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    text = "Вы администратор! Держите админ панель"
    markup = admin_main_panel_kb()
    await respond_user(event, text, markup)


@router.message(Command("admin"))
async def admin_panel_for_non_admins(message: Message):
    await message.answer("У вас нет прав администратора(")
