import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from game_share_bot.core.keyboards.buttons import _return_button
from game_share_bot.core.callbacks import MenuCallback
from game_share_bot.core.callbacks.subscription import SubscriptionCallback
from game_share_bot.domain.enums.subscription.action import SubscriptionAction
from game_share_bot.domain.enums.subscription.type import SubscriptionType


def subscription_actions_kb() -> InlineKeyboardMarkup:
    default_subscription_button = InlineKeyboardButton(
        text="Купить подписку",
        callback_data=SubscriptionCallback(
            action=SubscriptionAction.SELECT_DURATION,
            subscription_type=SubscriptionType.DEFAULT
        ).pack()
    )

    premium_subscription_button = InlineKeyboardButton(
        text="Купить премиум подписку",
        callback_data=SubscriptionCallback(
            action=SubscriptionAction.SELECT_DURATION,
            subscription_type=SubscriptionType.PREMIUM
        ).pack()
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [default_subscription_button],
            [premium_subscription_button],
            [_return_button(MenuCallback(section ="personal"))]
        ]
    )

def select_duration_kb(sub_type: SubscriptionType) -> InlineKeyboardMarkup:
    buttons = []
    duration_months = [1,2,3,6,12]
    for month in duration_months:
        buttons.append(
                InlineKeyboardButton(
                    text=f"{month} месяцев",
                    callback_data=SubscriptionCallback(
                        action=SubscriptionAction.CONFIRM_BUY,
                        subscription_type=sub_type,
                        month_duration=month
                    ).pack())
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def confirm_subscription_buy_kb(sub_type: SubscriptionType, duration: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Перейти к оплате", callback_data=SubscriptionCallback(
                action=SubscriptionAction.BUY,
                subscription_type=sub_type,
                month_duration=duration
            ).pack())],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=SubscriptionCallback(
                action=SubscriptionAction.INFO,
            ).pack())]
        ]
    )