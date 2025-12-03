from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from game_share_bot.core.callbacks import MenuCallback, AdminCallback
from game_share_bot.domain.enums import MenuSection, AdminAction


def return_button(callback: CallbackData) -> InlineKeyboardButton:
    return InlineKeyboardButton(text="⬅️ Назад", callback_data=callback.pack())


def to_main_menu_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text="⬅️ В главное меню", callback_data=MenuCallback(section=MenuSection.MAIN).pack())

def admin_button(text: str, action: AdminAction) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=AdminCallback(action=action).pack())
