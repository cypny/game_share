from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from game_share_bot.infrastructure.models.game import Game


def get_take_game_kb(games: list[Game]) -> InlineKeyboardMarkup:
    """Клавиатура с кнопками 'Взять' для каждой игры"""
    buttons = []

    for game in games:
        buttons.append([
            InlineKeyboardButton(
                text=f"🎮 Взять {game.title}",
                callback_data=f"take_game_{game.id}"
            )
        ])

    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)