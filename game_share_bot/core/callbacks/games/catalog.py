from aiogram.filters.callback_data import CallbackData


class CatalogCallback(CallbackData, prefix="catalog"):
    page: int = 0
