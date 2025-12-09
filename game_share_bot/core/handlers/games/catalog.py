from aiogram import F, Router, types
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import CatalogCallback
from game_share_bot.core.keyboards import catalog_keyboard
from game_share_bot.infrastructure.repositories import GameRepository
from game_share_bot.infrastructure.repositories.game_category import GameCategoryRepository
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.infrastructure.utils.formatting import format_games_list

router = Router()
logger = get_logger(__name__)


@router.callback_query(CatalogCallback.filter())
async def catalog(callback: CallbackQuery, callback_data: CatalogCallback, session: AsyncSession):
    try:
        query = callback_data.query
        page = callback_data.page

        if query == "__categories__":
            reply, reply_markup = await _process_categories(session, page=page)
        else:
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


@router.message(lambda message: not message.text.startswith("/"))
async def search_game(message: types.Message, session: AsyncSession):
    query = message.text
    page = 0
    reply, reply_markup = await _process_search_game(query, session, page=page)
    await message.answer(
        reply,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )


@router.message(F.text.startswith("/category_"))
async def category_games(message: types.Message, session: AsyncSession):
    try:
        category_id = int(message.text.split("_")[1])
    except (IndexError, ValueError):
        await message.answer("Некорректная категория")
        return

    query = f"cat:{category_id}"
    page = 0
    reply, reply_markup = await _process_search_game(query, session, page=page)
    await message.answer(
        reply,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )


async def _process_categories(
    session: AsyncSession, page: int = 0, page_size: int = 10
) -> tuple[str, InlineKeyboardMarkup]:
    category_repo = GameCategoryRepository(session)

    skip = page * page_size
    take = page_size

    categories = await category_repo.get_all(skip=skip, take=take)
    total_categories = await category_repo.count_all()

    if not categories:
        return "Категории не найдены", catalog_keyboard(page, total_categories, page_size, "__categories__")

    total_pages = (total_categories + page_size - 1) // page_size
    categories_lines = [f"/category_{c.id} — {c.name}" for c in categories]
    categories_str = "\n".join(categories_lines)
    reply = f"Категории игр ({page + 1}/{total_pages}):\n\n{categories_str}"

    return reply, catalog_keyboard(page, total_categories, page_size, "__categories__")


async def _process_search_game(
    query: str, session: AsyncSession, page: int = -1, page_size: int = 10
) -> tuple[str, InlineKeyboardMarkup]:
    game_repo = GameRepository(session)

    skip = page * page_size
    take = page_size

    if not query:
        games = await game_repo.get_all(skip=skip, take=take)
        games.sort(key=lambda game: game.title)
        total_games = await game_repo.count_all()
    elif query.startswith("cat:"):
        category_id = int(query.split(":", 1)[1])
        games, total_games = await game_repo.get_by_category(category_id=category_id, skip=skip, take=take)
    else:
        games, total_games = await game_repo.search_games(query, skip=skip, take=take)

    if total_games == 0:
        if query and query.startswith("cat:"):
            reply = "В этой категории пока нет игр"
        else:
            reply = "Игр не найдено"
        return reply, catalog_keyboard(page, total_games, page_size, query, hide_nav_buttons=True)

    total_pages = (total_games + page_size - 1) // page_size
    games_str = format_games_list(games)

    if query and query.startswith("cat:"):
        title = "Игры категории"
    else:
        title = "Каталог игр"

    reply = f"{title} ({page + 1}/{total_pages}):\n\n{games_str}"

    return reply, catalog_keyboard(page, total_games, page_size, query, hide_nav_buttons=page == -1)
