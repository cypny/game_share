from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import GameCallback
from game_share_bot.infrastructure.repositories import GameRepository
from game_share_bot.infrastructure.utils import format_game_full, get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(GameCallback.filter(F.action == "open"))
async def open_game_page(callback: CallbackQuery, callback_data: GameCallback, session: AsyncSession):
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} запросил информацию об игре: {callback_data.game_id}")

    try:
        game_repo = GameRepository(session)
        game_id = callback_data.game_id

        logger.debug(f"Поиск игры с ID: {game_id}")

        game = await game_repo.get_by_id(game_id)
        if game is None:
            logger.warning(f"Игра {game_id} не найдена для пользователя {user_id}")
            await callback.answer("Игра не найдена")
            return

        reply = format_game_full(game)
        await callback.message.answer_photo(
            caption=reply,
            parse_mode="HTML",
            photo=game.cover_image_url
        )
        logger.info(f"Информация об игре {game_id} отправлена пользователю {user_id}")
        return

    except ValueError:
        logger.warning(f"Неверный формат ID игры от пользователя {user_id}: {callback.message.text}")
        await callback.answer("❌ Неверный формат команды")
    except Exception as e:
        logger.error(f"Ошибка при получении информации об игре для пользователя {user_id}: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке информации об игре")


@router.message()
async def search_game(message: types.Message, session: AsyncSession):
    game_repo = GameRepository(session)

    text = message.text
    for game in await game_repo.get_all():
        if text.lower() in game.title.lower():
            reply = format_game_full(game)

            await message.answer_photo(
                caption=reply,
                parse_mode="HTML",
                photo=game.cover_image_url
            )
            return
    await message.answer("Не найдено")
