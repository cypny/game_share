from aiogram import F
from aiogram.filters.callback_data import CallbackData, CallbackQueryFilter

from game_share_bot.domain.enums.actions.game_actions import GameAction


class GameCallback(CallbackData, prefix="game"):
    game_id: int
    action: GameAction

    @classmethod
    def filter_by_action(cls, action: GameAction) -> CallbackQueryFilter:
        return cls.filter(F.action == action)
