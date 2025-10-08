from aiogram.filters.callback_data import CallbackData


class UserCallback(CallbackData, prefix="user"):
    action: str