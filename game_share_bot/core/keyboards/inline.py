from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from game_share_bot.core.callbacks import CatalogCallback, MenuCallback


def back_to_main_menu_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text="⬅️ Меню", callback_data=MenuCallback(section='main').pack())


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Каталог", callback_data=CatalogCallback().pack())],
            [InlineKeyboardButton(text="📦 Подписки", callback_data=MenuCallback(section='subs').pack())],
            [InlineKeyboardButton(text="🆘 Поддержка", callback_data="help")],
        ]
    )


def catalog_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [back_to_main_menu_button()]
        ]
    )
