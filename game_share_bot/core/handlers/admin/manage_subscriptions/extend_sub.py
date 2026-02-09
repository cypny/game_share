from typing import Optional
from datetime import datetime, timezone, timedelta
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.keyboards import return_to_admin_main_panel_kb
from game_share_bot.domain.enums import AdminAction
from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.infrastructure.repositories import SubscriptionRepository, UserRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter_by_action(AdminAction.EXTEND_SUBSCRIPTION), IsAdmin())
async def extend_subscription_start(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """Начало процесса продления подписки"""
    try:
        # Получаем данные из состояния
        data = await state.get_data()
        phone = data.get('phone')

        if not phone:
            logger.error("В данных состояния не найден номер телефона")
            await callback.answer("❌ Данные пользователя не найдены")
            await callback.message.edit_text(
                text="Произошла ошибка. Попробуйте снова.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        # Получаем пользователя и активную подписку
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

        await state.update_data(
            subscription_id=str(active_subscription.id),
            current_end_date=active_subscription.end_date.isoformat() if active_subscription.end_date else None
        )

        from game_share_bot.core.keyboards.inline.admin import create_extend_options_kb

        await callback.message.edit_text(
            text=f"📅 Продление подписки для пользователя {phone}\n\n"
                 f"Текущая дата окончания: {active_subscription.end_date.strftime('%d.%m.%Y') 
                 if active_subscription.end_date else 'не указана'}\n\n"
                 f"Выберите вариант продления",
            reply_markup=create_extend_options_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка в extend_subscription_start: {e}", exc_info=True)
        await callback.answer("Произошла ошибка")
        await callback.message.edit_text(
            text="❌ Произошла ошибка при начале продления подписки",
            reply_markup=return_to_admin_main_panel_kb()
        )


@router.callback_query(AdminCallback.filter_by_action(AdminAction.EXTEND_BY_MONTHS), IsAdmin())
async def extend_by_months(callback: CallbackQuery, callback_data: AdminCallback,
                           session: AsyncSession, state: FSMContext):
    """Продление на определенное количество месяцев"""
    try:
        months = getattr(callback_data, 'months', 1)

        data = await state.get_data()
        subscription_id = data.get('subscription_id')

        if not subscription_id:
            logger.error("В данных состояния не найден ID подписки")
            await callback.answer("❌ Данные подписки не найдены")
            return

        sub_repo = SubscriptionRepository(session)
        subscription = await sub_repo.get_by_id(subscription_id)
        if not subscription:
            await callback.answer("❌ Подписка не найдена")
            return

        current_end_date = subscription.end_date or datetime.now(timezone.utc)
        new_end_date = current_end_date + timedelta(days=30 * months)

        await state.update_data(new_end_date=new_end_date.isoformat())

        confirm_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Подтвердить продление",
                        callback_data=AdminCallback(
                            action=AdminAction.CONFIRM_EXTEND_SUBSCRIPTION
                        ).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data=AdminCallback(
                            action=AdminAction.RETURN_TO_MAIN_PANEL
                        ).pack()
                    )
                ]
            ]
        )

        await callback.message.edit_text(
            text=f"⚠️ Подтвердите продление подписки\n\n"
                 f"Текущая дата окончания: {subscription.end_date.strftime('%d.%m.%Y')}\n"
                 f"Новая дата окончания: {new_end_date.strftime('%d.%m.%Y')}\n"
                 f"Продление на: {months} месяцев\n\n"
                 f"Вы уверены, что хотите продлить подписку?",
            reply_markup=confirm_kb
        )

    except Exception as e:
        logger.error(f"Ошибка в extend_by_months: {e}", exc_info=True)
        await callback.answer("Произошла ошибка при расчете продления")

@router.callback_query(AdminCallback.filter_by_action(AdminAction.CONFIRM_EXTEND_SUBSCRIPTION), IsAdmin())
async def confirm_extend_subscription(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """Подтверждение и выполнение продления подписки"""
    try:
        data = await state.get_data()
        phone = data.get('phone')
        subscription_id = data.get('subscription_id')
        new_end_date_str = data.get('new_end_date')

        if not phone or not subscription_id or not new_end_date_str:
            logger.error(f"Недостаточно данных для продления: phone={phone}, "
                         f"subscription_id={subscription_id}, new_end_date={new_end_date_str}")
            await callback.answer("❌ Данные для продления не найдены")
            return

        new_end_date = datetime.fromisoformat(new_end_date_str)

        sub_repo = SubscriptionRepository(session)
        subscription = await sub_repo.get_by_id(subscription_id)
        if not subscription:
            await callback.answer("❌ Подписка не найдена")
            return

        old_end_date = subscription.end_date

        try:
            await sub_repo.update(subscription_id, end_date=new_end_date)

            logger.info(f"Продлена подписка для пользователя {phone}: "
                        f"{old_end_date.strftime('%d.%m.%Y')} -> {new_end_date.strftime('%d.%m.%Y')}")

        except Exception as update_error:
            logger.error(f"Ошибка обновления даты подписки: {update_error}")
            await session.rollback()
            await callback.answer("❌ Ошибка при продлении подписки")
            return

        await callback.answer("✅ Подписка продлена")

        await callback.message.edit_text(
            text=f"✅ Подписка успешно продлена для пользователя {phone}\n\n"
                 f"📅 Старая дата окончания: {old_end_date.strftime('%d.%m.%Y')}\n"
                 f"📅 Новая дата окончания: {new_end_date.strftime('%d.%m.%Y')}\n"
                 f"🔄 Подписка активна и продолжает действовать.",
            reply_markup=return_to_admin_main_panel_kb()
        )

        await state.update_data({
            'subscription_id': None,
            'current_end_date': None,
            'new_end_date': None
        })

    except Exception as e:
        logger.error(f"Ошибка в confirm_extend_subscription: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка")
        await callback.message.edit_text(
            text="❌ Произошла ошибка при продлении подписки",
            reply_markup=return_to_admin_main_panel_kb()
        )