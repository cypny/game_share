from aiogram import F
from aiogram.filters.callback_data import CallbackData, CallbackQueryFilter

from game_share_bot.domain.enums import MenuSection


class MenuCallback(CallbackData, prefix="menu"):
    section: MenuSection

    @classmethod
    def filter_by_section(cls, section: MenuSection) -> CallbackQueryFilter:
        return cls.filter(F.section == section)
