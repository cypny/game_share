from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from game_share_bot.core.callbacks import ConfirmationCallback, TakeDiscConfirmationCallback
from game_share_bot.core.keyboards.inline.buttons import return_button


def return_kb(callback: CallbackData) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [return_button(callback)]
        ]
    )


def confirmation_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=ConfirmationCallback(is_confirmed=True).pack())],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=ConfirmationCallback(is_confirmed=False).pack())]
        ]
    )


def take_disc_confirmation_kb(rental_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения взятия диска"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, я взял диск", callback_data=TakeDiscConfirmationCallback(rental_id=rental_id, is_confirmed=True).pack())],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=TakeDiscConfirmationCallback(rental_id=rental_id, is_confirmed=False).pack())]
        ]
    )

