from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks.user import UserCallback
from game_share_bot.core.keyboards import register_kb
from game_share_bot.core.states import RegisterState
from game_share_bot.infrastructure.repositories import UserRepository

router = Router()


@router.callback_query(UserCallback.filter(F.action == "register"))  # type: ignore
async def register(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()

    if await UserRepository(session).get_by_tg_id(callback.from_user.id):
        await callback.message.answer("Ты уже зарегистрирован!", reply_markup=ReplyKeyboardRemove())
    else:
        await callback.message.answer(
            "Пожалуйста, поделитесь номером телефона для регистрации",
            reply_markup=register_kb()
        )

        await state.set_state(RegisterState.waiting_for_phone)


@router.message(RegisterState.waiting_for_phone, F.content_type == ContentType.CONTACT)
async def handle_phone_number(message: Message, session: AsyncSession, state: FSMContext):
    user_repo = UserRepository(session)

    phone_number = message.contact.phone_number
    result = await user_repo.try_create(
        tg_id=message.from_user.id,
        phone=phone_number,
        name=message.from_user.username,
    )

    await state.clear()
    if result is None:
        await message.answer("Произошла непредвиденная ошибка! Обратись в поддержку",
                             reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(f"✅ Номер +{phone_number} сохранён! Регистрация завершена.",
                             reply_markup=ReplyKeyboardRemove())
