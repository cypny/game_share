from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.keyboards import return_kb
from game_share_bot.core.states import AppointState
from game_share_bot.infrastructure.repositories import UserRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter(F.action == "appoint"), IsAdmin())  # type: ignore
async def request_tg_id_for_appoint(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Введите telegram_id пользователя, которому хотите дать права администратора:",
                                     reply_markup=return_kb(AdminCallback(action="return_to_main")))
    await state.set_state(AppointState.waiting_for_tg_id)


@router.message(AppointState.waiting_for_tg_id, IsAdmin())
async def appoint_admin(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()

    try:
        tg_id = int(message.text)
    except ValueError:
        return await message.answer("Некорректный ввод, telegram_id должен содержать только цифры")

    result = await UserRepository(session).make_admin(tg_id)
    if result:
        return await message.answer(f"Права администратора успешно выданы пользователю {tg_id}")

    return await message.answer(f"Пользователь {tg_id} не найден, возможно он не зарегистрирован\n\n"
                                f"Роль администратора можно выдать только зарегистрированным пользователям")
