from aiogram.filters.callback_data import CallbackData


class ConfirmationCallback(CallbackData, prefix="game"):
    is_confirmed: bool
