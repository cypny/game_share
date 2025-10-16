from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks.subscription import SubscriptionCallback
from game_share_bot.core.keyboards import (
    return_kb,
    subscription_actions_kb,
    select_duration_kb,
    confirm_subscription_buy_kb
)
from game_share_bot.domain.enums.subscription.action import SubscriptionAction
from game_share_bot.infrastructure.models import SubscriptionPlan
from game_share_bot.infrastructure.repositories import SubscriptionRepository
from game_share_bot.infrastructure.repositories import UserRepository
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.infrastructure.utils.formatting import format_subscription_info, format_subscription_plan

router = Router()
logger = get_logger(__name__)


@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.INFO))
async def subscription_info_and_buying(callback: CallbackQuery, session: AsyncSession):
    user_repo = UserRepository(session)
    sub_repo = SubscriptionRepository(session)
    user = await user_repo.get_by_tg_id(callback.from_user.id)
    subscription = await sub_repo.get_by_user(user)

    await callback.answer()
    await callback.message.edit_text(
        text=format_subscription_info(subscription),
        reply_markup=subscription_actions_kb(),
        parse_mode="HTML"
    )


@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.SELECT_DURATION))
async def select_subscription_duration(
        callback: CallbackQuery,
        callback_data: SubscriptionCallback,
        session: AsyncSession):
    sub_type = callback_data.subscription_type
    sub_plan = await session.scalar(
        select(SubscriptionPlan).where(SubscriptionPlan.name == sub_type)
    )
    message = (f"Подписка:\n\n"
               f"{format_subscription_plan(sub_plan)}\n\n"
               f"Выберите длительность")
    await callback.answer()
    await callback.message.edit_text(
        text=message,
        reply_markup=select_duration_kb(sub_type),
        parse_mode="HTML"
    )


@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.CONFIRM_BUY))
async def confirm_subscription_buy(
        callback: CallbackQuery,
        callback_data: SubscriptionCallback):
    plan_name = callback_data.subscription_type
    duration = callback_data.month_duration
    message = (f"Подтвердите данные:\n"
               f"Уровень подписки: {plan_name}\n"
               f"Длительность: {duration}")
    await callback.answer()
    await callback.message.edit_text(
        text=message,
        reply_markup=confirm_subscription_buy_kb(callback_data.subscription_type, callback_data.month_duration),
        parse_mode="HTML"
    )


@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.BUY))
async def purchase_subscription(callback: CallbackQuery, callback_data: SubscriptionCallback):
    await callback.answer()
    await callback.message.edit_text(
        text=f"Пока не реализовано: подписка {callback_data.subscription_type} {callback_data.month_duration} месяцев",
        reply_markup=return_kb(SubscriptionCallback(action=SubscriptionAction.INFO)),
    )
