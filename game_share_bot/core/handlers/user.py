from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types  import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.keyboards.inline import request_contact_kb
from game_share_bot.core.states import RegisterState
from game_share_bot.infrastructure.repositories import UserRepository

router = Router()

@router.callback_query(F.data == "register")
async def register(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите свой номер телефона")
    await state.set_state(RegisterState.waiting_for_phone)
    await callback.answer()

@router.message(RegisterState.waiting_for_phone)
async def handle_phone_number(message: Message, session: AsyncSession):
    user_repo = UserRepository(session)

    phone_number = message.text
    result = await user_repo.try_create(
        tg_id=message.from_user.id,
        phone=phone_number,
        name=message.from_user.username,
    )

    if result is None:
        return await message.answer("Телефон уже занят либо ты уже зарегистрирован")

    return await message.answer(
        f"✅ Номер {phone_number} сохранён! Регистрация завершена."
    )
