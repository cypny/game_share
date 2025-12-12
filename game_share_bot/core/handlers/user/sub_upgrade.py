import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import SubscriptionCallback
from game_share_bot.core.keyboards.inline.subscription import confirm_subscription_upgrade_kb, payment_redirect_kb
from game_share_bot.core.services.check_payment import check_payment_polling
from game_share_bot.core.services.sub_upgrade import calculate_additional_payment
from game_share_bot.domain.enums import SubscriptionAction
from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.domain.payment.yookassa_service import create_upgrade_payment
from game_share_bot.infrastructure.models import SubscriptionPlan
from game_share_bot.infrastructure.repositories import SubscriptionRepository, UserRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)

@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.UPGRADE))
async def sub_upgrade_info(callback: CallbackQuery, callback_data: SubscriptionCallback, session: AsyncSession, state: FSMContext):
    sub_plan: SubscriptionPlan = await session.scalar(
        select(SubscriptionPlan)
        .where(SubscriptionPlan.id == callback_data.subscription_type)
    )
    await state.update_data(sub_plan_id=sub_plan.id, sub_plan_name=sub_plan.name)

    await callback.answer()
    await callback.message.edit_text(
        text=(f"Апгрейд подписки до уровня {sub_plan.name}. "
              f"При апгрейде вы доплачиваете разницу до стоимости нового тарифа, а срок подписки не сбрасывается."),
        reply_markup=confirm_subscription_upgrade_kb()
    )

@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.BUY_UPGRADE))
async def purchase_upgrade(callback: CallbackQuery, callback_data: SubscriptionCallback, session: AsyncSession, state: FSMContext):
    user_repo = UserRepository(session)
    sub_repo = SubscriptionRepository(session)
    user = await user_repo.get_by_tg_id(callback.from_user.id)
    current_sub = await sub_repo.get_active_by_user(user)
    if not current_sub:
        await callback.answer("У вас нет подписки для апгрейда")
        return


    sub_data = await state.get_data()

    target_plan_id = sub_data["sub_plan_id"]
    target_plan = await session.scalar(
        select(SubscriptionPlan)
        .where(SubscriptionPlan.id == target_plan_id)
    )

    try:
        payment_id, confirmation_url = await create_upgrade_payment(current_sub, target_plan, user)
    except Exception as err:
        logger.error(err, exc_info=True)
        await callback.answer("Не удалось обновить подписку, попробуйте позже")
        return

    subscription = await sub_repo.create(
        user_id=user.id,
        plan_id=target_plan.id,
        yookassa_payment_id=payment_id,
        status=SubscriptionStatus.PENDING_PAYMENT,
        start_date=current_sub.start_date,
        end_date=current_sub.end_date,
        is_auto_renewal=False
    )
    if subscription:
        await callback.message.edit_text(
            text=f"Апгрейд подписк с уровня {current_sub.plan.name} до {target_plan.name}.",
            reply_markup=payment_redirect_kb(confirmation_url),
        )
    else:
        logger.error(f"Ошибка при создании подписки {subscription}")
    asyncio.create_task(check_payment_polling(payment_id))


