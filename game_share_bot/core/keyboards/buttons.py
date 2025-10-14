from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def _return_button(callback: CallbackData) -> InlineKeyboardButton:
    return InlineKeyboardButton(text="⬅️ Назад", callback_data=callback.pack())


def return_kb(callback: CallbackData) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_return_button(callback)]
        ]
    )