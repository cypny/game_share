from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎮 Игры", callback_data="menu_games"),
                InlineKeyboardButton(text="📦 Подписки", callback_data="menu_orders")
            ]
        ]
    )