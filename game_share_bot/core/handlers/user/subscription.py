import asyncio
from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks.subscription import SubscriptionCallback
from game_share_bot.core.keyboards import (
    confirm_subscription_buy_kb,
    return_kb,
    select_duration_kb,
    subscription_actions_kb,
)
from game_share_bot.core.keyboards.inline.subscription import payment_redirect_kb
from game_share_bot.core.services.check_payment import check_payment_polling
from game_share_bot.core.states.subscription.subscribe import SubscriptionState
from game_share_bot.domain.enums.subscription.action import SubscriptionAction
from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.domain.payment.yookassa_service import create_payment, get_payment_status
from game_share_bot.infrastructure.models import SubscriptionPlan
from game_share_bot.infrastructure.repositories import SubscriptionRepository, UserRepository
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.infrastructure.utils.formatting import format_subscription_info, format_subscription_plan
from game_share_bot.scheduler.job_container import job_container

router = Router()
logger = get_logger(__name__)


@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.INFO))
async def subscription_info_and_buying(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user_repo = UserRepository(session)
    sub_repo = SubscriptionRepository(session)
    try:
        user = await user_repo.get_by_tg_id(callback.from_user.id)
        if user is None:
            await callback.answer("Необходима регистрация")
            return
        subscriptions = await sub_repo.get_all_by_user(user)
        active_sub = None
        for sub in subscriptions:
            if sub.status == SubscriptionStatus.ACTIVE:
                active_sub = sub
        plans = await session.scalars(
            select(SubscriptionPlan)
        )

        plan_infos = [{"id": plan.id, "name": plan.name, "cost": plan.monthly_price} for plan in plans]
        await callback.answer()
        await callback.message.edit_text(
            text=format_subscription_info(active_sub),
            reply_markup=subscription_actions_kb(plan_infos, active_sub),
            parse_mode="HTML"
        )

        await state.set_state(SubscriptionState.choosing_plan)
    except Exception as e:
        await callback.answer("Ошибка")
        logger.error(e)
        return


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
        state: FSMContext, ):
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
async def purchase_subscription(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    sub_repo = SubscriptionRepository(session)
    user_repo = UserRepository(session)

    user = await user_repo.get_by_tg_id(callback.from_user.id)

    subs = await sub_repo.get_all_by_user(user)
    for sub in subs:
        if sub.status == SubscriptionStatus.ACTIVE:
            await callback.answer("Вы уже имеете подписку")
            return

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
        status=SubscriptionStatus.PENDING_PAYMENT,
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

    asyncio.create_task(check_payment_polling(payment_id))
    await state.clear()

