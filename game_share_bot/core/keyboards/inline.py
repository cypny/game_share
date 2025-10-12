from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from game_share_bot.core.callbacks import CatalogCallback, AdminCallback, MenuCallback


def _return_button(callback: CallbackData) -> InlineKeyboardButton:
    return InlineKeyboardButton(text="⬅️ Назад", callback_data=callback.pack())


def return_kb(callback: CallbackData) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_return_button(callback)]
        ]
    )


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Каталог", callback_data=CatalogCallback().pack())],
            [InlineKeyboardButton(text="📦 Подписки", callback_data=MenuCallback(section='subs').pack())],
            [InlineKeyboardButton(text="🆘 Поддержка", callback_data="help")],
        ]
    )


def admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # [
            #     InlineKeyboardButton(text="Добавить игру", callback_data=AdminCallback(action='add_game').pack()),
            #     InlineKeyboardButton(text="Удалить игру", callback_data=AdminCallback(action='delete_game').pack())
            # ],
            # [
            #     InlineKeyboardButton(text="Добавить диск", callback_data=AdminCallback(action='add_disk').pack()),
            #     InlineKeyboardButton(text="Удалить диск", callback_data=AdminCallback(action='delete_disk').pack())
            # ],
            # [
            #     InlineKeyboardButton(text="Добавить категорию",
            #                          callback_data=AdminCallback(action='add_category').pack()),
            #     InlineKeyboardButton(text="Удалить категорию",
            #                          callback_data=AdminCallback(action='delete_category').pack())
            # ],
            [
                InlineKeyboardButton(text="Выдать админку", callback_data=AdminCallback(action='appoint').pack())
            ]
        ]

    )
