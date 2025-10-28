from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import MenuCallback
from game_share_bot.core.keyboards import personal_cabinet_kb
from game_share_bot.domain.enums import MenuSection
from game_share_bot.infrastructure.repositories import UserRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(MenuCallback.filter_by_section(MenuSection.PERSONAL_CABINET))
async def personal_cabinet(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} открыл личный кабинет")

    try:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_tg_id(user_id)

        if not user:
            logger.warning(f"Пользователь {user_id} не найден при открытии личного кабинета")
            await callback.answer("❌ Пользователь не найден")
            return

        text = f"👤 Личный кабинет\n\nВаш номер телефона: {user.phone}"
        markup = personal_cabinet_kb()

        await callback.message.edit_text(text, reply_markup=markup)
        logger.info(f"Личный кабинет успешно открыт для пользователя {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при открытии личного кабинета для пользователя {user_id}: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке личного кабинета")


@router.callback_query(MenuCallback.filter_by_section(MenuSection.MANAGE_SUBSCRIPTION))
async def manage_subscription(callback: CallbackQuery):
    """Обработчик кнопки 'Управление подпиской'"""
    await callback.answer("📦 Функционал 'Управление подпиской' в разработке")
