from aiogram import F
from aiogram.filters.callback_data import CallbackData, CallbackQueryFilter

from game_share_bot.domain.enums import AdminAction


class AdminCallback(CallbackData, prefix="admin"):
    action: AdminAction
    page: int = 0

    @classmethod
    def filter_by_action(cls, action: AdminAction) -> CallbackQueryFilter:
        return cls.filter(F.action == action)
