from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from core.callbacks import CatalogCallback
from game_share_bot.core.keyboards import catalog_kb
from game_share_bot.infrastructure.repositories import GameRepository
from game_share_bot.infrastructure.utils import format_game_short, format_game_full, get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(CatalogCallback.filter())
async def catalog(callback: CallbackQuery, callback_data: CatalogCallback, session: AsyncSession):
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} открыл каталог")

    try:
        game_repo = GameRepository(session)
        games = await game_repo.get_all()

        logger.debug(f"Получено {len(games)} игр для пользователя {user_id}")
        games_str = "\n\n---\n\n".join(format_game_short(game) for game in games)
        reply = "Каталог (все игры пока что): \n" + games_str

        await callback.answer()
        await callback.message.edit_text(reply, parse_mode="HTML", reply_markup=catalog_kb(games))
        logger.info(f"Каталог успешно отправлен пользователю {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при получении каталога для пользователя {user_id}: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке каталога")

