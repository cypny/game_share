from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks.subscription import SubscriptionCallback
from game_share_bot.domain.enums.subscription.action import SubscriptionAction
from game_share_bot.core.callbacks import MenuCallback
from game_share_bot.core.keyboards.inline import personal_cabinet_kb, subscription_actions_kb
from game_share_bot.infrastructure.repositories import UserRepository
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.infrastructure.repositories import SubscriptionRepository
from game_share_bot.infrastructure.utils.formatting import format_subscription

router = Router()
logger = get_logger(__name__)


@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.INFO))
async def subscription_info_and_buying(
        callback: CallbackQuery,
        callback_data: SubscriptionCallback,
        session: AsyncSession
):
    user_repo = UserRepository(session)
    sub_repo = SubscriptionRepository(session)
    user = await user_repo.get_by_tg_id(callback.from_user.id)
    subscription = await sub_repo.get_by_user(user)

    await callback.answer()
    await callback.message.edit_text(
        text=format_subscription(subscription),
        reply_markup=subscription_actions_kb()
    )


@router.callback_query(SubscriptionCallback.filter(F.action == SubscriptionAction.SELECT_DURATION))
async def select_subscription_duration(callback: CallbackQuery, callback_data: SubscriptionCallback,
                                       session: AsyncSession):
    pass
