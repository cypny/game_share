from aiogram.types import InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.infrastructure.models import Game
from game_share_bot.infrastructure.models.game import GameCategory
from game_share_bot.infrastructure.repositories import GameRepository
from game_share_bot.infrastructure.repositories.game_category import GameCategoryRepository


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


async def try_parse_categories(message_text: str, session: AsyncSession) -> list[GameCategory] | None:
    category_names = message_text.split(',')
    game_categories = []
    repo = GameCategoryRepository(session)
    for category_name in category_names:
        category = await repo.get_by_name(category_name)
        if category is None:
            return None
        game_categories.append(category)

    return game_categories if game_categories else None
