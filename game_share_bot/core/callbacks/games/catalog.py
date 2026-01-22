from aiogram.filters.callback_data import CallbackData


class CatalogCallback(CallbackData, prefix="catalog"):
    query: str = ""
    page: int = 0
    category_id: int | None = None
