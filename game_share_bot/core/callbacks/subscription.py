from typing import Optional

from aiogram.filters.callback_data import CallbackData

from game_share_bot.domain.enums.subscription.action import SubscriptionAction
from game_share_bot.domain.enums.subscription.type import SubscriptionType


class SubscriptionCallback(CallbackData, prefix="sub"):
    action: SubscriptionAction
    month_duration: Optional[int] = None

    subscription_type: Optional[SubscriptionType] = None

