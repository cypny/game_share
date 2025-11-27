from aiogram.types import InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.infrastructure.models import Game
from game_share_bot.infrastructure.repositories import GameRepository


async def try_get_game_by_id_in_message(
        message: Message, session: AsyncSession, return_kb: InlineKeyboardMarkup
    ) -> Game | None:
    try:
        game_id = int(message.text)
    except ValueError:
        await message.answer("ID должно быть числом", reply_markup=return_kb)
        return None

    game = await GameRepository(session).get_by_id(game_id)
    if game is None:
        await message.answer(f"Игра с ID = {game_id} не найдена", reply_markup=return_kb)
        return None

    return game
