from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton


def return_button(callback: CallbackData) -> InlineKeyboardButton:
    return InlineKeyboardButton(text="⬅️ Назад", callback_data=callback.pack())
