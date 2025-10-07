from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.keyboards import get_take_game_kb
from game_share_bot.infrastructure.repositories import GameRepository, DiscRepository, RentalRepository, UserRepository
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
        reply = "Каталог игр: \n" + games_str

        await callback.answer()
        await callback.message.edit_text(
            reply,
            parse_mode="HTML",
            reply_markup=get_take_game_kb(games)
        )
        logger.info(f"Каталог успешно отправлен пользователю {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при получении каталога для пользователя {user_id}: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке каталога")


@router.callback_query(F.data.startswith("take_game_"))
async def take_game(callback: CallbackQuery, session: AsyncSession):
    """Обработчик кнопки 'Взять игру'"""
    user_id = callback.from_user.id
    game_id = int(callback.data.split("_")[2])

    logger.info(f"Пользователь {user_id} пытается взять игру {game_id}")

    try:
        # Получаем репозитории
        game_repo = GameRepository(session)
        disc_repo = DiscRepository(session)
        rental_repo = RentalRepository(session)
        user_repo = UserRepository(session)

        # Проверяем существование пользователя
        user = await user_repo.get_by_tg_id(user_id)
        if not user:
            await callback.answer("❌ Сначала нужно зарегистрироваться")
            return

        # Проверяем доступность дисков
        available_disc = await disc_repo.get_available_disc_by_game(game_id)
        if not available_disc:
            await callback.answer("❌ Все диски этой игры заняты")
            return

        # Получаем информацию об игре
        game = await game_repo.get_by_id(game_id)
        if not game:
            await callback.answer("❌ Игра не найдена")
            return

        # Создаем аренду и обновляем статус диска
        await rental_repo.create_rental(user.id, available_disc.disc_id)
        await disc_repo.update_disc_status(available_disc.disc_id, 2)  # 2 = rented

        logger.info(f"Пользователь {user_id} успешно взял игру {game_id} (диск {available_disc.disc_id})")
        await callback.answer(f"✅ Вы успешно взяли игру '{game.title}'!")

    except Exception as e:
        logger.error(f"Ошибка при взятии игры {game_id} пользователем {user_id}: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при взятии игры")


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
