from aiogram.filters.callback_data import CallbackData


class RentalCallback(CallbackData, prefix="rental"):
    """Callback для операций с арендой дисков"""
    action: str
    rental_id: int