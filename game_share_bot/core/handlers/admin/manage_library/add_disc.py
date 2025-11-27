from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import AdminCallback, ConfirmationCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.handlers.utils import cancel_admin_action
from game_share_bot.core.keyboards import confirmation_kb
from game_share_bot.core.keyboards.inline.admin import return_to_admin_manage_library_panel_kb
from game_share_bot.core.services.admin import try_get_game_by_id_in_message
from game_share_bot.core.states import AddDiscState
from game_share_bot.domain.enums import AdminAction
from game_share_bot.infrastructure.repositories import DiscRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter_by_action(AdminAction.ADD_DISK), IsAdmin())
async def request_id_for_adding_disc(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Введите id игры которой хотите добавить диск:",
                                     reply_markup=return_to_admin_manage_library_panel_kb())
    await state.set_state(AddDiscState.waiting_for_id)


@router.message(AddDiscState.waiting_for_id, IsAdmin())
async def handle_id_and_request_confirmation_for_adding_disc(message: Message, session: AsyncSession,
                                                             state: FSMContext):
    game = await try_get_game_by_id_in_message(message, session, return_to_admin_manage_library_panel_kb())
    await state.update_data({"game_id": game.id})
    await message.answer(f"Подтвердите добавление диска к игре {game.title}", reply_markup=confirmation_kb())
    await state.set_state(AddDiscState.waiting_for_confirmation)


@router.callback_query(AddDiscState.waiting_for_confirmation, ConfirmationCallback.filter_confirmed(), IsAdmin())
async def add_disc(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    game_id = data["game_id"]
    disc_repo = DiscRepository(session)
    result = await disc_repo.add_disc(game_id)
    await callback.answer()

    if result is None:
        await callback.message.edit_text("Не получилось добавить диск(",
                                         reply_markup=return_to_admin_manage_library_panel_kb())
    else:
        disc_count = await disc_repo.get_disc_count_by_game(game_id)
        await callback.message.edit_text("Диск успешно добавлен!\n"
                                         f"Кол-во дисков у игры {game_id}: {disc_count}",
                                         reply_markup=return_to_admin_manage_library_panel_kb())

    await state.clear()

@router.callback_query(AddDiscState.waiting_for_confirmation, ConfirmationCallback.filter_canceled())
async def cancel_disc_add(callback: CallbackQuery, state: FSMContext):
    await cancel_admin_action(callback, state)
