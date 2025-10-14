from typing import Optional

from aiogram.filters.callback_data import CallbackData

from game_share_bot.domain.enums.subscription.type import SubscriptionType


class SubscriptionCallback(CallbackData, prefix="subscription"):
    action: str
    subscription_type: Optional[SubscriptionType] = None
    month_duration: Optional[int] = None
