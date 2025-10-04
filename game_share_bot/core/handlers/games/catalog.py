from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.keyboards import catalog_kb
from game_share_bot.infrastructure.repositories import GameRepository
from game_share_bot.infrastructure.utils import format_game_short, format_game_full, get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(F.data == "catalog")
async def catalog(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} открыл каталог")

    try:
        game_repo = GameRepository(session)
        games = await game_repo.get_all()

        logger.debug(f"Получено {len(games)} игр для пользователя {user_id}")
        games_str = "\n\n---\n\n".join(format_game_short(game) for game in games)
        reply = "Каталог (все игры пока что): \n" + games_str

        await callback.answer()
        await callback.message.edit_text(reply, parse_mode="HTML", reply_markup=catalog_kb())
        logger.info(f"Каталог успешно отправлен пользователю {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при получении каталога для пользователя {user_id}: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке каталога")


@router.message(F.text.startswith("/game_"))
async def cmd_game(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил информацию об игре: {message.text}")

    try:
        game_repo = GameRepository(session)
        game_id = int(message.text.split('_')[1])

        logger.debug(f"Поиск игры с ID: {game_id}")

        game = await game_repo.get_by_id(game_id)
        if game is None:
            logger.warning(f"Игра {game_id} не найдена для пользователя {user_id}")
            await message.answer("Игра не найдена")
            return

        reply = format_game_full(game)
        await message.answer_photo(
            caption=reply,
            parse_mode="HTML",
            photo=game.cover_image_url
        )
        logger.info(f"Информация об игре {game_id} отправлена пользователю {user_id}")

    except ValueError:
        logger.warning(f"Неверный формат ID игры от пользователя {user_id}: {message.text}")
        await message.answer("❌ Неверный формат команды")
    except Exception as e:
        logger.error(f"Ошибка при получении информации об игре для пользователя {user_id}: {str(e)}", exc_info=True)
        await message.answer("❌ Ошибка при загрузке информации об игре")
