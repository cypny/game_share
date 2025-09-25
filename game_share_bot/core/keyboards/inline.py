from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.callbacks import MenuCallback

def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎮 Каталог", callback_data="catalog"),
                InlineKeyboardButton(text="📦 Подписки", callback_data=MenuCallback(section="subs").pack())
            ]
        ]
    )

def catalog_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Меню", callback_data=MenuCallback(section="main").pack())]
        ]
    )