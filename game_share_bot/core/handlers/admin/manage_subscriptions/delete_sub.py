from datetime import timezone
from typing import Optional
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.keyboards import return_to_admin_main_panel_kb
from game_share_bot.core.keyboards.inline.admin import confirm_remove_subscription_kb
from game_share_bot.domain.enums import AdminAction
from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.infrastructure.repositories import SubscriptionRepository, UserRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter_by_action(AdminAction.REMOVE_SUBSCRIPTION), IsAdmin())
async def confirm_remove_subscription(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """Подтверждение удаления подписки"""
    try:
        data = await state.get_data()
        phone = data.get('phone')

        if not phone:
            logger.error("Phone not found in state data")
            await callback.answer("❌ Данные пользователя не найдены")
            await callback.message.edit_text(
                text="Произошла ошибка. Попробуйте снова.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        user_repo = UserRepository(session)
        user = await user_repo.get_by_phone(phone)
        if not user:
            await callback.answer("❌ Пользователь не найден")
            await callback.message.edit_text(
                text=f"Пользователь с номером {phone} не найден.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        sub_repo = SubscriptionRepository(session)
        active_subscription = await sub_repo.get_active_by_user(user)

        if not active_subscription:
            await callback.answer("❌ У пользователя нет активных подписок")
            await callback.message.edit_text(
                text=f"У пользователя {phone} нет активных подписок.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        await state.update_data(subscription_id=str(active_subscription.id))

        from datetime import datetime
        start_date = active_subscription.start_date.strftime("%d.%m.%Y") if active_subscription.start_date else "неизвестно"
        end_date = active_subscription.end_date.strftime("%d.%m.%Y") if active_subscription.end_date else "неизвестно"

        await callback.message.edit_text(
            text=f"⚠️ Вы уверены, что хотите удалить подписку у пользователя {phone}?\n\n"
                 f"📋 Информация о подписке:\n"
                 f"• Дата начала: {start_date}\n"
                 f"• Дата окончания: {end_date}\n"
                 f"После удаления подписка будет помечена как завершенная.",
            reply_markup=confirm_remove_subscription_kb()
        )

    except Exception as e:
        logger.error(f"Error in confirm_remove_subscription: {e}", exc_info=True)
        await callback.answer("Произошла ошибка")
        await callback.message.edit_text(
            text="❌ Произошла ошибка при подтверждении удаления",
            reply_markup=return_to_admin_main_panel_kb()
        )


@router.callback_query(AdminCallback.filter_by_action(AdminAction.CONFIRM_REMOVE_SUBSCRIPTION), IsAdmin())
async def execute_remove_subscription(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """Выполнение удаления подписки"""
    try:
        data = await state.get_data()
        phone = data.get('phone')
        subscription_id = data.get('subscription_id')

        if not phone or not subscription_id:
            logger.error(f"Missing data in state: phone={phone}, subscription_id={subscription_id}")
            await callback.answer("❌ Данные не найдены")
            await callback.message.edit_text(
                text="Произошла ошибка. Попробуйте снова.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        sub_repo = SubscriptionRepository(session)
        subscription = await sub_repo.get_by_id(subscription_id)

        if not subscription:
            await callback.answer("❌ Подписка не найдена")
            await callback.message.edit_text(
                text="Подписка не найдена. Возможно, она уже была удалена.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        try:
            updated_subscription = await sub_repo.update(
                subscription.id,
                status=SubscriptionStatus.ENDED
            )

        except Exception as update_error:
            logger.error(f"Error updating subscription status: {update_error}")
            await callback.answer("❌ Ошибка при обновлении статуса")
            await callback.message.edit_text(
                text="Не удалось обновить статус подписки.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        await callback.answer("✅ Подписка удалена")

        from datetime import datetime
        end_date = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M")

        await callback.message.edit_text(
            text=f"✅ Подписка успешно удалена у пользователя {phone}\n\n"
                 f"📋 Подписка помечена как завершенная:\n"
                 f"• Время завершения: {end_date}\n"
                 f"• Новый статус: {SubscriptionStatus.ENDED.name}",
            reply_markup=return_to_admin_main_panel_kb()
        )

        await state.update_data(subscription_id=None)

    except Exception as e:
        logger.error(f"Error in execute_remove_subscription: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка")
        await callback.message.edit_text(
            text="❌ Произошла ошибка при удалении подписки",
            reply_markup=return_to_admin_main_panel_kb()
        )