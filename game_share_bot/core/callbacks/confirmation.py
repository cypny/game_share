from aiogram import F
from aiogram.filters.callback_data import CallbackData, CallbackQueryFilter


class ConfirmationCallback(CallbackData, prefix="game"):
    is_confirmed: bool

    @classmethod
    def filter_confirmed(cls) -> CallbackQueryFilter:
        return cls.filter(F.is_confirmed)

    @classmethod
    def filter_canceled(cls) -> CallbackQueryFilter:
        return cls.filter(F.is_confirmed == False)


class TakeDiscConfirmationCallback(CallbackData, prefix="take_disc_confirm"):
    """Callback для подтверждения взятия диска"""
    rental_id: int
    is_confirmed: bool

    @classmethod
    def filter_confirmed(cls) -> CallbackQueryFilter:
        return cls.filter(F.is_confirmed)

    @classmethod
    def filter_canceled(cls) -> CallbackQueryFilter:
        return cls.filter(F.is_confirmed == False)

