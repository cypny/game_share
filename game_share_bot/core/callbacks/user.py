from aiogram.filters.callback_data import CallbackData, CallbackQueryFilter

from game_share_bot.domain.enums.user_action import UserAction


class UserCallback(CallbackData, prefix="user"):
    action: UserAction

    @classmethod
    def filter_by_action(cls, action: UserAction) -> CallbackQueryFilter:
        return cls.filter(F.action == action)  # type: ignore