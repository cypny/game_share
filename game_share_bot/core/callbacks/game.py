from aiogram.filters.callback_data import CallbackData


class GameCallback(CallbackData, prefix="game"):
    action: str
    game_id: int
