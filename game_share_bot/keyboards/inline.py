from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callbacks import MenuCallback

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎮 Каталог", callback_data="catalog"),
                InlineKeyboardButton(text="📦 Подписки", callback_data=MenuCallback(section="subs").pack())
            ]
        ]
    )

def catalog() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Меню", callback_data=MenuCallback(section="main").pack())]
        ]
    )