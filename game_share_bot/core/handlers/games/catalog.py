from aiogram import Router, types
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import CatalogCallback, MenuCallback
from game_share_bot.core.keyboards import return_kb, catalog_keyboard
from game_share_bot.domain.enums import MenuSection
from game_share_bot.infrastructure.repositories import GameRepository
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.infrastructure.utils.formatting import format_games_list

router = Router()
logger = get_logger(__name__)


@router.callback_query(CatalogCallback.filter())
async def catalog(callback: CallbackQuery, callback_data: CatalogCallback, session: AsyncSession):
    try:
        query = callback_data.query
        page = callback_data.page
        reply, reply_markup = await _process_search_game(query, page, session)

        await callback.answer()
        await callback.message.edit_text(
            reply,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

    except Exception as e:
        await callback.answer("❌ Ошибка при загрузке каталога")

@router.message(lambda message: not message.text.startswith('/'))
async def search_game(message: types.Message, session: AsyncSession):
    query = message.text
    page = 0
    reply, reply_markup = await _process_search_game(query, page, session)
    await message.answer(
        reply,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def _process_search_game(query: str, page:int, session: AsyncSession) -> tuple[str, InlineKeyboardMarkup]:
    game_repo = GameRepository(session)
    page_size = 2
    if not query:
        games = await game_repo.get_all(
            skip=page * page_size,
            take=page_size
        )
        total_games = await game_repo.count_all()
    else:
        games, total_games = await game_repo.search_games(
            query,
            skip=page * page_size,
            take=page_size
        )

    games_str = format_games_list(games)
    reply = f"Каталог игр:\n\n{games_str}"

    return reply, catalog_keyboard(page, total_games, page_size, query)


