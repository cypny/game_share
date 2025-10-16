from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.keyboards.inline.buttons import return_button
from game_share_bot.domain.enums import AdminAction


def get_game_detail_kb(game_id: int, is_available: bool = True) -> InlineKeyboardMarkup:
    """Клавиатура для страницы конкретной игры"""
    buttons = []

    if is_available:
        buttons.append([
            InlineKeyboardButton(
                text="🎮 Взять игру",
                callback_data=f"take_game_{game_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def add_game_image_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                return_button(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL)),
                InlineKeyboardButton(text="Пропустить",
                                     callback_data=AdminCallback(action=AdminAction.SKIP_IMAGE_INPUT).pack())
            ]
        ]
    )
