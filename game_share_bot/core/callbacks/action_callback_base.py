from abc import ABC
from enum import StrEnum
from typing import TypeVar

from aiogram import F
from aiogram.filters.callback_data import CallbackQueryFilter

E = TypeVar("E", bound=StrEnum)

# после того как я это написал, подумал, что это уже перебор, но в будущем, если колбэков с action
# станет больше, то можно будет использовать, чтобы выполнялся DRY и все такое
#
# зато пафосно
class ActionCallback[E](ABC):
    action: E

    @classmethod
    def filter_by_action(cls, action: E) -> CallbackQueryFilter:
        return cls.filter(F.action == action)  # type: ignore
