from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class CatalogCallback(CallbackData, prefix="catalog"):
    pass