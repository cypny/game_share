from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from game_share_bot.core.callbacks import MenuCallback, SubscriptionCallback
from game_share_bot.core.keyboards.inline.buttons import return_button
from game_share_bot.domain.enums import MenuSection, SubscriptionAction


def subscription_actions_kb(plan_infos) -> InlineKeyboardMarkup:
    sub_buttons = []
    for plan_info in plan_infos:
        sub_buttons.append(
            [
                InlineKeyboardButton(
                    text=f"Купить подписку {plan_info['name']}",
                    callback_data=SubscriptionCallback(
                        action=SubscriptionAction.SELECT_DURATION,
                        subscription_type=plan_info['id']
                    ).pack()
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *sub_buttons,
            [return_button(MenuCallback(section=MenuSection.PERSONAL_CABINET))]
        ]
    )


def select_duration_kb() -> InlineKeyboardMarkup:
    buttons = []
    duration_months = [1, 2, 3, 6, 12]
    for month in duration_months:
        buttons.append(
            InlineKeyboardButton(
                text=f"{month} месяцев",
                callback_data=SubscriptionCallback(
                    action=SubscriptionAction.CONFIRM_BUY,
                    month_duration=month
                ).pack())
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def confirm_subscription_buy_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Перейти к оплате",
                callback_data=SubscriptionCallback(
                        action=SubscriptionAction.BUY
                    ).pack())],
            [InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=SubscriptionCallback(
                        action=SubscriptionAction.INFO,
                    ).pack())]
        ]
    )

def payment_redirect_kb(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Перейти на страницу оплаты", url=url)],
            [InlineKeyboardButton(text="Оплатил", callback_data=SubscriptionCallback(action=SubscriptionAction.CONFIRM_YOOKASSA_PAYMENT).pack())],
            [return_button(SubscriptionCallback(action=SubscriptionAction.INFO))]
        ]
    )
