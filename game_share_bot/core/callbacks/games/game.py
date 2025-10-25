from aiogram.filters.callback_data import CallbackData

from game_share_bot.core.callbacks.action_callback_base import ActionCallback
from game_share_bot.domain.enums.actions.game_actions import GameAction


class GameCallback(CallbackData, ActionCallback[GameAction], prefix="game"):
    action: GameAction
    game_id: int
