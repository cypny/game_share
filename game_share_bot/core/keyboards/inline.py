from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from game_share_bot.core.callbacks import CatalogCallback, GameCallback, UserCallback, MenuCallback
from game_share_bot.infrastructure.models import Game


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Каталог", callback_data=CatalogCallback().pack())],
            [InlineKeyboardButton(text="📦 Подписки", callback_data=MenuCallback(section="subs").pack())],
            [InlineKeyboardButton(text="👤 Регистрация", callback_data=UserCallback(action="register").pack())],
            [InlineKeyboardButton(text="🆘 Поддержка", callback_data="help")],
        ]
    )


def catalog_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Меню", callback_data=MenuCallback(section="main").pack())]
        ]
    )
