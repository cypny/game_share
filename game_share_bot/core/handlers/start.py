from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.handlers.menu.main import main_menu
from game_share_bot.core.keyboards import main_menu_kb, register_kb
from game_share_bot.core.states import RegisterState
from game_share_bot.infrastructure.repositories import UserRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    logger.info(f"Команда /start от пользователя {message.from_user.id} (@{message.from_user.username})")

    if await UserRepository(session).get_by_tg_id(message.from_user.id):
        logger.debug(f"Пользователь {message.from_user.id} уже зарегистрирован - отправлено меню")
        await main_menu(message)
    else:
        await message.answer("Пожалуйста, поделитесь номером телефона для регистрации", reply_markup=register_kb())
        await state.set_state(RegisterState.waiting_for_phone)


@router.message(RegisterState.waiting_for_phone, F.content_type == ContentType.CONTACT)
async def handle_phone_number(message: Message, session: AsyncSession, state: FSMContext):
    user_repo = UserRepository(session)

    phone_number = message.contact.phone_number
    if phone_number[0] != '+':
        phone_number = '+' + phone_number

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
        await message.answer(f"✅ Номер {phone_number} сохранён! Регистрация завершена.",
                             reply_markup=ReplyKeyboardRemove())
        await message.answer("Главное меню", reply_markup=main_menu_kb())
