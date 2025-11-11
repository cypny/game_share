from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from game_share_bot.core.callbacks.subscription import SubscriptionCallback
from game_share_bot.core.keyboards import (
    return_kb,
    subscription_actions_kb,
    select_duration_kb,
    confirm_subscription_buy_kb
)
from game_share_bot.core.keyboards.inline.subscription import payment_redirect_kb
from game_share_bot.core.states.subscription.subscribe import SubscriptionState
from game_share_bot.domain.enums.subscription.action import SubscriptionAction
from game_share_bot.domain.yookassa import create_payment
from game_share_bot.infrastructure.models import SubscriptionPlan
from game_share_bot.infrastructure.repositories import SubscriptionRepository
from game_share_bot.infrastructure.repositories import UserRepository
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.infrastructure.utils.formatting import format_subscription_info, format_subscription_plan

router = Router()
logger = get_logger(__name__)


@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.INFO))
async def subscription_info_and_buying(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user_repo = UserRepository(session)
    sub_repo = SubscriptionRepository(session)
    user = await user_repo.get_by_tg_id(callback.from_user.id)
    subscription = await sub_repo.get_by_user(user)

    plans = await session.scalars(
        select(SubscriptionPlan)
    )

    plan_infos = [{"id": plan.id, "name": plan.name} for plan in plans]
    await callback.answer()
    await callback.message.edit_text(
        text=format_subscription_info(subscription),
        reply_markup=subscription_actions_kb(plan_infos),
        parse_mode="HTML"
    )

    await state.set_state(SubscriptionState.choosing_plan)


@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.SELECT_DURATION))
async def select_subscription_duration(
        callback: CallbackQuery,
        callback_data: SubscriptionCallback,
        session: AsyncSession,
        state: FSMContext):
    sub_type = callback_data.subscription_type
    sub_plan = await session.scalar(
        select(SubscriptionPlan).where(SubscriptionPlan.id == sub_type)
    )

    await state.update_data(plan_id=sub_plan.id, plan_name=sub_plan.name)

    message = (f"Подписка:\n\n"
               f"{format_subscription_plan(sub_plan)}\n\n"
               f"Выберите длительность")
    await callback.answer()
    await callback.message.edit_text(
        text=message,
        reply_markup=select_duration_kb(),
        parse_mode="HTML"
    )

    await state.set_state(SubscriptionState.choosing_duration)


@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.CONFIRM_BUY))
async def confirm_subscription_buy(
        callback: CallbackQuery,
        callback_data: SubscriptionCallback,
        state: FSMContext,):
    await state.update_data(duration=callback_data.month_duration)

    sub_data = await state.get_data()

    message = (f"Подтвердите данные:\n"
               f"Уровень подписки: {sub_data["plan_name"]}\n"
               f"Длительность: {sub_data["duration"]}\n")
    await callback.answer()
    await callback.message.edit_text(
        text=message,
        reply_markup=confirm_subscription_buy_kb(),
        parse_mode="HTML"
    )

    await state.set_state(SubscriptionState.confirming)


@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.BUY))
async def purchase_subscription(callback: CallbackQuery, callback_data: SubscriptionCallback, session: AsyncSession, state: FSMContext):
    sub_repo = SubscriptionRepository(session)
    user_repo = UserRepository(session)

    user = await user_repo.get_by_tg_id(callback.from_user.id)

    sub_data = await state.get_data()


    sub_plan = await session.scalar(
        select(SubscriptionPlan).where(SubscriptionPlan.id == sub_data["plan_id"])
    )
    current_date = datetime.now(timezone.utc)
    end_date = current_date + timedelta(days=30 * sub_data["duration"])

    try:
        payment_id, confirmation_url = await create_payment(
            sub_plan,
            sub_data["duration"],
            user
        )
    except Exception as e:
        logger.error(e)
        await callback.answer("Не удалось создать платеж, попробуйте позже")
        raise
    subscription = await sub_repo.create(
        user_id=user.id,
        plan_id=sub_data['plan_id'],
        yookassa_payment_id=payment_id,
        start_date=current_date,
        end_date=end_date,
        is_auto_renewal=False
    )

    if subscription:
        await callback.answer()
        await callback.message.edit_text(
            text=f"Оплатите подписку: подписка {sub_data['plan_name']} {sub_data['duration']} месяцев",
            reply_markup=payment_redirect_kb(confirmation_url),
        )
    else:
        await callback.answer("Ошибка")

    await state.clear()
