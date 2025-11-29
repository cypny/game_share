from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, default_state
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import CatalogCallback
from game_share_bot.core.keyboards import catalog_keyboard
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
        reply, reply_markup = await _process_search_game(query, session, page=page)

        await callback.answer()
        await callback.message.edit_text(
            reply,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

    except Exception as e:
        logger.error(f"Ошибка при загрузке каталога: {e}")
        await callback.answer("❌ Ошибка при загрузке каталога")


# TODO: слишком общий хэндлер, ловит чего не должен - ломает логику назначения админа
# надо думать как исправить - можно оставить, и использовать FSMContext где ломает,
# или создать раздел "поиск игры"
@router.message(lambda message: not message.text.startswith('/'))
async def search_game(message: types.Message, session: AsyncSession):
    query = message.text
    page = 0
    reply, reply_markup = await _process_search_game(query, session, page=page)
    await message.answer(
        reply,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )


async def _process_search_game(
        query: str,
        session: AsyncSession,
        page=-1,
        page_size=10
) -> tuple[str, InlineKeyboardMarkup]:
    game_repo = GameRepository(session)

    skip = page * page_size
    take = page_size

    if not query:
        games = await game_repo.get_all(
            skip=skip,
            take=take
        )
        games.sort(key=lambda game: game.title)
        total_games = await game_repo.count_all()
    else:
        games, total_games = await game_repo.search_games(
            query,
            skip=skip,
            take=take
        )

    total_pages = (total_games + page_size - 1) // page_size
    games_str = format_games_list(games)
    reply = f"Каталог игр ({page + 1}/{total_pages}):\n\n{games_str}"

    return reply, catalog_keyboard(page, total_games, page_size, query, hide_nav_buttons=page == -1)
