from aiogram import Router, types
from aiogram.types import CallbackQuery, Message
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
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} открыл каталог")

    try:
        game_repo = GameRepository(session)
        page = callback_data.page
        page_size = 5

        games = await game_repo.get_all(
            skip=page * page_size,
            take=page_size
        )

        total_games = await game_repo.count_all()

        logger.debug(f"Получено {len(games)} игр для пользователя {user_id}")

        games_str = format_games_list(games)
        reply = f"Каталог игр:\n\n{games_str}"

        await callback.answer()
        await callback.message.edit_text(
            reply,
            parse_mode="HTML",
            reply_markup=catalog_keyboard(page, total_games, page_size)
        )
        logger.info(f"Каталог успешно отправлен пользователю {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при получении каталога для пользователя {user_id}: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке каталога")

# @router.message()
# async def search_game(message: types.Message, session: AsyncSession):
#     game_repo = GameRepository(session)
#
#     text = message.text
#     for game in await game_repo.get_all():
#         if text.lower() in game.title.lower():
#             reply = format_game_full(game)
#
#             await message.answer_photo(
#                 caption=reply,
#                 parse_mode="HTML",
#                 photo=game.cover_image_url
#             )
#             return
#     await message.answer("Не найдено")


