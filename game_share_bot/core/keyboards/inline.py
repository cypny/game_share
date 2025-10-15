from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from game_share_bot.core.callbacks import CatalogCallback, AdminCallback, MenuCallback
from game_share_bot.core.callbacks.confirmation import ConfirmationCallback
from game_share_bot.domain.enums import AdminAction


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
            [InlineKeyboardButton(text="👤 Личный кабинет", callback_data=MenuCallback(section='personal').pack())],
            [InlineKeyboardButton(text="🆘 Поддержка", callback_data="help")],
        ]
    )


def personal_cabinet_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Арендованные диски", callback_data=MenuCallback(section='rented_disks').pack())],
            [InlineKeyboardButton(text="📦 Управление подпиской", callback_data=MenuCallback(section='manage_subscription').pack())],
            [InlineKeyboardButton(text="📋 Моя очередь", callback_data=MenuCallback(section='my_queue').pack())],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=MenuCallback(section='main').pack())]
        ]
    )


def admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавить игру",
                                     callback_data=AdminCallback(action=AdminAction.ADD_GAME).pack()),
                InlineKeyboardButton(text="Удалить игру",
                                     callback_data=AdminCallback(action=AdminAction.DELETE_GAME).pack())
            ],
            [
                InlineKeyboardButton(text="Выдать админку",
                                     callback_data=AdminCallback(action=AdminAction.APPOINT).pack())
            ],
            [
                InlineKeyboardButton(text="📋 Запросы на возврат",
                                     callback_data=AdminCallback(action=AdminAction.VIEW_RETURN_REQUESTS).pack())
            ]
        ]
    )


def confirmation_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=ConfirmationCallback(is_confirmed=True).pack())],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=ConfirmationCallback(is_confirmed=False).pack())]
        ]
    )


def add_game_image_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _return_button(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL)),
                InlineKeyboardButton(text="Пропустить",
                                     callback_data=AdminCallback(action=AdminAction.SKIP_IMAGE_INPUT).pack())
            ]
        ]
    )


def return_to_admin_panel_kb() -> InlineKeyboardMarkup:
    return return_kb(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL))