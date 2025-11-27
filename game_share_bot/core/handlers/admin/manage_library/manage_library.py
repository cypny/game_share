from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.handlers.utils import respond_user
from game_share_bot.core.keyboards.inline.admin import admin_manage_library_kb
from game_share_bot.domain.enums import AdminAction
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter_by_action(AdminAction.MANAGE_LIBRARY), IsAdmin())
async def admin_manage_library_panel(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await respond_user(event, "Управление библиотекой", admin_manage_library_kb())





