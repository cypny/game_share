from typing import Optional, List
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.keyboards import return_to_admin_main_panel_kb
from game_share_bot.core.keyboards.inline.admin import select_sub_plan_kb, confirm_change_plan_kb
from game_share_bot.domain.enums import AdminAction
from game_share_bot.infrastructure.models import SubscriptionPlan
from game_share_bot.infrastructure.repositories import SubscriptionRepository, UserRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter_by_action(AdminAction.CHANGE_SUBSCRIPTION_TYPE), IsAdmin())
async def change_subscription_type(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """Начало процесса изменения типа подписки"""
    try:
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
            current_subscription_id=str(active_subscription.id),
            current_plan_id=active_subscription.plan_id
        )

        plans = await session.scalars(select(SubscriptionPlan))
        plan_infos = [(plan.name, plan.id) for plan in plans]

        if not plan_infos:
            await callback.answer("❌ Нет доступных тарифных планов")
            await callback.message.edit_text(
                text="Нет доступных тарифных планов для изменения.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        current_plan = await session.get(SubscriptionPlan, active_subscription.plan_id)
        current_plan_name = current_plan.name if current_plan else "Неизвестный тариф"

        await callback.message.edit_text(
            text=f"📋 Текущий тариф пользователя {phone}: {current_plan_name}\n\n"
                 f"Выберите новый тип подписки:",
            reply_markup=select_sub_plan_kb(plan_infos, is_new_plan=True)
        )

    except Exception as e:
        logger.error(f"Ошибка в change_subscription_type: {e}", exc_info=True)
        await callback.answer("Произошла ошибка")
        await callback.message.edit_text(
            text="❌ Произошла ошибка при начале изменения типа подписки",
            reply_markup=return_to_admin_main_panel_kb()
        )


@router.callback_query(AdminCallback.filter_by_action(AdminAction.SELECT_NEW_PLAN), IsAdmin())
async def confirm_change_plan(callback: CallbackQuery, callback_data: AdminCallback,
                              session: AsyncSession, state: FSMContext):
    """Подтверждение изменения типа подписки"""
    try:
        new_plan_id: Optional[int] = getattr(callback_data, 'plan_id', None)
        if not new_plan_id:
            logger.warning("Нет plan_id в callback_data")
            await callback.answer("Не выбран тарифный план")
            return

        data = await state.get_data()
        phone = data.get('phone')
        current_plan_id = data.get('current_plan_id')
        current_subscription_id = data.get('current_subscription_id')

        if not phone or not current_plan_id or not current_subscription_id:
            logger.error(f"Недостаточно данных в состоянии: phone={phone}, "
                         f"current_plan_id={current_plan_id}, current_subscription_id={current_subscription_id}")
            await callback.answer("❌ Данные не найдены")
            await callback.message.edit_text(
                text="Произошла ошибка. Попробуйте снова.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        current_plan = await session.get(SubscriptionPlan, current_plan_id)
        new_plan = await session.get(SubscriptionPlan, new_plan_id)

        if not current_plan or not new_plan:
            await callback.answer("❌ Тарифный план не найден")
            await callback.message.edit_text(
                text="Один из тарифных планов не найден.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        await state.update_data(new_plan_id=new_plan_id)

        current_price = f"{current_plan.monthly_price} руб." if current_plan.monthly_price else "Бесплатно"
        new_price = f"{new_plan.monthly_price} руб." if new_plan.monthly_price else "Бесплатно"

        await callback.message.edit_text(
            text=f"⚠️ Вы уверены, что хотите изменить тариф у пользователя {phone}?\n\n"
                 f"📋 Текущий тариф:\n"
                 f"• Название: {current_plan.name}\n"
                 f"• Цена: {current_price}\n"
                 f"• Описание: {current_plan.description or 'Нет описания'}\n\n"
                 f"📋 Новый тариф:\n"
                 f"• Название: {new_plan.name}\n"
                 f"• Цена: {new_price}\n"
                 f"• Описание: {new_plan.description or 'Нет описания'}\n\n"
                 f"Примечание: Дата окончания подписки не изменится.",
            reply_markup=confirm_change_plan_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка в confirm_change_plan: {e}", exc_info=True)
        await callback.answer("Произошла ошибка")
        await callback.message.edit_text(
            text="❌ Произошла ошибка при подтверждении изменения тарифа",
            reply_markup=return_to_admin_main_panel_kb()
        )


@router.callback_query(AdminCallback.filter_by_action(AdminAction.CONFIRM_CHANGE_PLAN), IsAdmin())
async def execute_change_plan(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """Выполнение изменения типа подписки"""
    try:
        data = await state.get_data()
        phone = data.get('phone')
        current_subscription_id = data.get('current_subscription_id')
        new_plan_id = data.get('new_plan_id')

        if not phone or not current_subscription_id or not new_plan_id:
            logger.error(f"Недостаточно данных в состоянии: phone={phone}, "
                         f"current_subscription_id={current_subscription_id}, new_plan_id={new_plan_id}")
            await callback.answer("❌ Данные не найдены")
            await callback.message.edit_text(
                text="Произошла ошибка. Попробуйте снова.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        sub_repo = SubscriptionRepository(session)
        subscription = await sub_repo.get_by_id(current_subscription_id)

        if not subscription:
            await callback.answer("❌ Подписка не найдена")
            await callback.message.edit_text(
                text="Подписка не найдена. Возможно, она уже была изменена или удалена.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        old_plan = await session.get(SubscriptionPlan, subscription.plan_id)
        new_plan = await session.get(SubscriptionPlan, new_plan_id)

        if not old_plan or not new_plan:
            await callback.answer("❌ Тарифный план не найден")
            await callback.message.edit_text(
                text="Один из тарифных планов не найден.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        try:
            await sub_repo.update(subscription.id, plan_id=new_plan_id)

            logger.info(f"Изменен тип подписки для пользователя {phone}: "
                        f"{old_plan.name} -> {new_plan.name}")

        except Exception as update_error:
            logger.error(f"Ошибка обновления типа подписки: {update_error}")
            await session.rollback()
            await callback.answer("❌ Ошибка при обновлении тарифа")
            await callback.message.edit_text(
                text="Не удалось изменить тип подписки.",
                reply_markup=return_to_admin_main_panel_kb()
            )
            return

        await callback.answer("✅ Тариф изменен")

        end_date = subscription.end_date.strftime("%d.%m.%Y") if subscription.end_date else "неизвестно"

        old_price = f"{old_plan.monthly_price} руб." if old_plan.monthly_price else "Бесплатно"
        new_price = f"{new_plan.monthly_price} руб." if new_plan.monthly_price else "Бесплатно"

        await callback.message.edit_text(
            text=f"✅ Тип подписки успешно изменен у пользователя {phone}\n\n"
                 f"📋 Старый тариф:\n"
                 f"• {old_plan.name} ({old_price})\n\n"
                 f"📋 Новый тариф:\n"
                 f"• {new_plan.name} ({new_price})\n\n"
                 f"📅 Дата окончания подписки: {end_date}\n"
                 f"🔄 Подписка сохранила свой статус и дату окончания.",
            reply_markup=return_to_admin_main_panel_kb()
        )

        await state.update_data({
            'current_subscription_id': None,
            'current_plan_id': None,
            'new_plan_id': None
        })

    except Exception as e:
        logger.error(f"Ошибка в execute_change_plan: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка")
        await callback.message.edit_text(
            text="❌ Произошла ошибка при изменении типа подписки",
            reply_markup=return_to_admin_main_panel_kb()
        )