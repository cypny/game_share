from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.keyboards import return_kb, return_to_admin_panel_kb
from game_share_bot.core.states import AppointState
from game_share_bot.domain.enums import AdminAction
from game_share_bot.infrastructure.repositories import UserRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter_by_action(AdminAction.APPOINT), IsAdmin())
async def request_tg_id_for_appoint(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Введите telegram_id пользователя, которому хотите дать права администратора:",
                                     reply_markup=return_kb(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL)))
    await state.set_state(AppointState.waiting_for_tg_id)


@router.message(AppointState.waiting_for_tg_id, IsAdmin())
async def appoint_admin(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()

    try:
        tg_id = int(message.text)
    except ValueError:
        answer_text = "Некорректный ввод, telegram_id должен содержать только цифры"
    else:
        result = await UserRepository(session).make_admin(tg_id)
        if result:
            answer_text = f"Права администратора успешно выданы пользователю {tg_id}"
        else:
            answer_text = (f"Пользователь {tg_id} не найден, возможно он не зарегистрирован\n\n"
                           f"Роль администратора можно выдать только зарегистрированным пользователям")

    await message.answer(answer_text, reply_markup=return_to_admin_panel_kb())
