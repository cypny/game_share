from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from game_share_bot.core.callbacks import GameCallback, MenuCallback
from game_share_bot.core.keyboards.inline.buttons import return_button
from game_share_bot.domain.enums import MenuSection
from game_share_bot.domain.enums.actions.game_actions import GameAction
from game_share_bot.infrastructure.utils import get_logger


def enter_queue_kb(game_id: int, is_available: bool = True) -> InlineKeyboardMarkup:
    """Клавиатура для страницы конкретной игры"""
    buttons = []
    logger = get_logger(__name__)
    logger.warning(is_available)
    if is_available:
        buttons.append([
            InlineKeyboardButton(
                text="🎮 Встать в очередь",
                callback_data=GameCallback(action=GameAction.REQUEST_QUEUE, game_id=game_id).pack(),
            )
        ])

    buttons.append([return_button(MenuCallback(section=MenuSection.MAIN))])

    return InlineKeyboardMarkup(inline_keyboard=buttons)