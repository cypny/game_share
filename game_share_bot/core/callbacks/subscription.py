from aiogram.filters.callback_data import CallbackData

from game_share_bot.domain.enums import SubscriptionAction, SubscriptionType


class SubscriptionCallback(CallbackData, prefix="sub"):
    action: SubscriptionAction
    month_duration: int | None = None
    subscription_type: SubscriptionType | None = None
