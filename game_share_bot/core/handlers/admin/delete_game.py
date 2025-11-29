from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import AdminCallback, ConfirmationCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.handlers.utils import cancel_admin_action
from game_share_bot.core.keyboards import confirmation_kb, return_to_admin_panel_kb
from game_share_bot.core.states import DeleteGameState
from game_share_bot.domain.enums import AdminAction
from game_share_bot.infrastructure.repositories import DiscRepository, GameRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter_by_action(AdminAction.DELETE_GAME), IsAdmin())
async def request_game_id(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Это экспериментальная функция. Наверное, она может что-то сломать\n\n"
                                     "Вряд-ли она вообще нужна, но если очень хочется - введите ID игры для удаления:",
                                     reply_markup=return_to_admin_panel_kb())
    await state.set_state(DeleteGameState.waiting_for_id)


@router.message(DeleteGameState.waiting_for_id, IsAdmin())
async def handle_id_and_request_confirmation(message: Message, session: AsyncSession, state: FSMContext):
    try:
        game_id = int(message.text)
    except ValueError:
        return await message.answer("ID должно быть числом", reply_markup=return_to_admin_panel_kb())

    game = await GameRepository(session).get_by_id(game_id)
    if game is None:
        return await message.answer(f"Игра с ID = {game_id} не найдена", reply_markup=return_to_admin_panel_kb())

    have_disc = await DiscRepository(session).get_by_field("game_id", game_id)
    if have_disc:
        return await message.answer("Найдены диски, привязанные к игре\n"
                                    "Невозможно удалить игру с привязанными дисками",
                                    reply_markup=return_to_admin_panel_kb())

    await state.update_data({"game_id": game_id})
    await message.answer(f"Подтвердите удаление игры {game.title}", reply_markup=confirmation_kb())
    return await state.set_state(DeleteGameState.waiting_for_confirmation)


@router.callback_query(DeleteGameState.waiting_for_confirmation,
                       ConfirmationCallback.filter_confirmed(),  # type: ignore
                       IsAdmin())
async def delete_game(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    game_id = await state.get_value("game_id")
    await callback.answer()

    result = await GameRepository(session).delete(game_id)
    if result:
        await callback.message.edit_text("Игра успешно удалена", reply_markup=return_to_admin_panel_kb())
    else:
        await callback.message.edit_text("Что-то пошло не по плану(", reply_markup=return_to_admin_panel_kb())
    await state.clear()


@router.callback_query(DeleteGameState.waiting_for_confirmation,
                       ConfirmationCallback.filter_canceled())  # type: ignore
async def cancel_game_delete(callback: CallbackQuery, state: FSMContext):
    await cancel_admin_action(callback, state)
