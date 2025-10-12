from aiogram import F
from aiogram.filters.callback_data import CallbackData

from game_share_bot.domain.enums.admin_action import AdminAction


class AdminCallback(CallbackData, prefix="admin"):
    action: AdminAction

    @classmethod
    def filter_by_action(cls, action: AdminAction):
        return cls.filter(F.action == action) # type: ignore
