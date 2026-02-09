from datetime import datetime, timezone, timedelta
from typing import Optional

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.keyboards import return_to_admin_main_panel_kb
from game_share_bot.core.keyboards.inline.admin import select_sub_plan_kb
from game_share_bot.core.services.admin import format_subscriber_message, format_subscriptions_message
from game_share_bot.core.states.admin.give_sub import GiveSubState
from game_share_bot.core.states.admin.manage_subscribers import ManageSubscribersState
from game_share_bot.domain.enums import AdminAction
from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.infrastructure.models import SubscriptionPlan
from game_share_bot.infrastructure.repositories import SubscriptionRepository, UserRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter_by_action(AdminAction.GIVE_SUB), IsAdmin())
async def give_sub(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    try:
        plans = await session.scalars(
            select(SubscriptionPlan)
        )
        plan_infos = [(plan.name, plan.id) for plan in plans]

        data = await state.get_data()
        has_active_sub = data.get("has_active_sub")
        if has_active_sub:
            await callback.answer("У пользователя уже есть активная подписка")
            return

        await callback.message.edit_text(
            text="Выберите тип подписки для выдачи",
            reply_markup=select_sub_plan_kb(plan_infos)
        )
    except Exception as e:
        logger.error(f"Error in give_sub: {e}", exc_info=True)
        await callback.answer("Произошла ошибка при загрузке тарифов")
        await callback.message.answer(
            text="Произошла ошибка",
            reply_markup=return_to_admin_main_panel_kb()
        )


@router.callback_query(AdminCallback.filter_by_action(AdminAction.SELECT_PLAN), IsAdmin())
async def select_duration(callback: CallbackQuery, callback_data: AdminCallback,
                          session: AsyncSession, state: FSMContext):
    try:
        plan_id: Optional[int] = getattr(callback_data, 'plan_id', None)
        if not plan_id:
            logger.warning(f"Нет плана в callback: {callback_data}")
            await callback.answer("Не выбран тарифный план")
            return

        plan = await session.get(SubscriptionPlan, plan_id)
        if not plan:
            logger.warning(f"Тарифный план с id {plan_id} не найден")
            await callback.answer("Тарифный план не найден")
            return

        await state.update_data(plan_id=plan_id)
        await state.set_state(GiveSubState.waiting_for_duration)

        await callback.answer()
        await callback.message.edit_text(
            text="Введите длительность подписки в месяцах",
            reply_markup=return_to_admin_main_panel_kb()
        )
    except Exception as e:
        logger.error(f"Ошибка при выборе длительности: {e}", exc_info=True)
        await callback.answer("Произошла ошибка")
        await callback.message.answer(
            text="Произошла ошибка при выборе тарифа",
            reply_markup=return_to_admin_main_panel_kb()
        )


@router.message(GiveSubState.waiting_for_duration, IsAdmin())
async def create_sub(message: Message, session: AsyncSession, state: FSMContext):
    try:
        try:
            duration_months = int(message.text.strip())
            if duration_months <= 0:
                await message.answer("❌ Длительность должна быть положительным числом")
                return
        except ValueError:
            await message.answer("❌ Введите корректное число месяцев")
            return

        data = await state.get_data()
        plan_id = data.get("plan_id")
        phone = data.get('phone')

        if not plan_id or not phone:
            logger.error(f"Missing data in state: plan_id={plan_id}, phone={phone}")
            await message.answer("❌ Данные не найдены. Начните процесс заново.")
            await state.clear()
            return

        plan = await session.get(SubscriptionPlan, plan_id)
        if not plan:
            logger.error(f"Plan with id {plan_id} not found")
            await message.answer("❌ Тарифный план не найден")
            return

        user_repo = UserRepository(session)
        user = await user_repo.get_by_phone(phone)
        if not user:
            logger.error(f"User with phone {phone} not found")
            await message.answer(f"❌ Пользователь с номером {phone} не найден")
            return

        sub_repo = SubscriptionRepository(session)
        current_date = datetime.now(timezone.utc)
        end_date = current_date + timedelta(days=30 * duration_months)

        subscription = await sub_repo.create(
            user_id=user.id,
            plan_id=plan_id,
            yookassa_payment_id=None,
            status=SubscriptionStatus.ACTIVE,
            start_date=current_date,
            end_date=end_date,
            is_auto_renewal=False
        )

        if subscription:
            end_date_str = end_date.strftime("%d.%m.%Y")
            await message.answer(
                text=f"✅ Подписка успешно выдана пользователю {phone}\n"
                     f"• Тариф: {plan.name}\n"
                     f"• Длительность: {duration_months} месяцев\n"
                     f"• Действует до: {end_date_str}",
                reply_markup=return_to_admin_main_panel_kb()
            )

            await state.clear()
        else:
            logger.error(f"Failed to create subscription for user {user.id}")
            await message.answer(
                text="❌ Не удалось создать подписку. Попробуйте еще раз.",
                reply_markup=return_to_admin_main_panel_kb()
            )
    except KeyError as e:
        logger.error(f"Missing key in state data: {e}")
        await message.answer("❌ Отсутствуют необходимые данные. Начните сначала.")
        await state.clear()
    except Exception as e:
        logger.error(f"Error in create_sub: {e}", exc_info=True)
        await message.answer(
            text="❌ Произошла ошибка при создании подписки",
            reply_markup=return_to_admin_main_panel_kb()
        )
        await state.clear()