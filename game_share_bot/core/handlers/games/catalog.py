from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession


from game_share_bot.core.callbacks import CatalogCallback, MenuCallback
from game_share_bot.core.keyboards import return_kb, get_game_detail_kb
from game_share_bot.infrastructure.repositories import GameRepository, DiscRepository, RentalRepository, UserRepository
from game_share_bot.infrastructure.utils import get_logger


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

        # Форматируем игры в нужном стиле
        games_list = []
        for game in games:
            game_text = f"🎮 {game.title}\n\n{game.description}\n\n<code>/game_{game.id}</code>"
            games_list.append(game_text)

        games_str = "\n\n---\n\n".join(games_list)
        reply = f"Каталог игр ({len(games)}):\n\n{games_str}"

        await callback.answer()
        await callback.message.edit_text(
            reply,
            parse_mode="HTML",
            reply_markup=return_kb(MenuCallback(section="main"))  # Используем старую работающую клавиатуру
        )
        logger.info(f"Каталог успешно отправлен пользователю {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при получении каталога для пользователя {user_id}: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке каталога")



@router.message(F.text.startswith("/game_"))
async def cmd_game(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил информацию об игре: {message.text}")

    try:
        game_repo = GameRepository(session)
        disc_repo = DiscRepository(session)
        rental_repo = RentalRepository(session)
        user_repo = UserRepository(session)

        game_id = int(message.text.split('_')[1])
        logger.debug(f"Поиск игры с ID: {game_id}")

        game = await game_repo.get_by_id(game_id)
        if game is None:
            logger.warning(f"Игра {game_id} не найдена для пользователя {user_id}")
            await message.answer("Игра не найдена")
            return

        # Получаем информацию о пользователе
        user = await user_repo.get_by_tg_id(user_id)

        # Получаем количество доступных дисков
        available_discs_count = await disc_repo.get_available_discs_count_by_game(game_id)

        # Проверяем, есть ли у пользователя активная аренда этой игры
        has_active_rental = False
        if user:
            active_rental = await rental_repo.get_active_rental_by_user_and_game(user.id, game_id)
            has_active_rental = active_rental is not None

        # Формируем информацию о доступности
        if has_active_rental:
            availability_text = "✅ Вы уже взяли эту игру"
            is_available = False
        elif available_discs_count > 0:
            availability_text = f"✅ Доступно дисков: {available_discs_count}"
            is_available = True
        else:
            availability_text = "❌ Все диски заняты"
            is_available = False

        # Форматируем полную информацию об игре
        reply = (
            f"🎮 <b>{game.title}</b>\n\n"
            f"{game.description}\n\n"
            f"{availability_text}\n\n"
            f"<code>/game_{game.id}</code>"
        )

        # Отправляем фото с описанием и соответствующей кнопкой
        if game.cover_image_url:
            await message.answer_photo(
                photo=game.cover_image_url,
                caption=reply,
                parse_mode="HTML",
                reply_markup=get_game_detail_kb(game.id, is_available and not has_active_rental)
            )
        else:
            await message.answer(
                reply,
                parse_mode="HTML",
                reply_markup=get_game_detail_kb(game.id, is_available and not has_active_rental)
            )

        logger.info(f"Информация об игре {game_id} отправлена пользователю {user_id}")

    except ValueError:
        logger.warning(f"Неверный формат ID игры от пользователя {user_id}: {message.text}")
        await message.answer("❌ Неверный формат команды. Используйте: /game_1")
    except Exception as e:
        logger.error(f"Ошибка при получении информации об игре для пользователя {user_id}: {str(e)}", exc_info=True)
        await message.answer("❌ Ошибка при загрузке информации об игре")


@router.callback_query(F.data.startswith("take_game_"))
async def take_game(callback: CallbackQuery, session: AsyncSession):
    """Обработчик кнопки 'Взять игру' на странице игры"""
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

        # Проверяем, нет ли у пользователя уже активной аренды этой игры
        existing_rental = await rental_repo.get_active_rental_by_user_and_game(user.id, game_id)
        if existing_rental:
            await callback.answer("❌ У вас уже есть эта игра на руках")
            return

        # Проверяем доступность дисков
        available_disc = await disc_repo.get_available_disc_by_game(game_id)
        logger.info(f"Найден доступный диск: {available_disc}")

        if not available_disc:
            await callback.answer("❌ Все диски этой игры заняты")
            return

        # Получаем информацию об игре
        game = await game_repo.get_by_id(game_id)
        if not game:
            await callback.answer("❌ Игра не найдена")
            return

        logger.info(f"Создание аренды: user_id={user.id}, disc_id={available_disc.disc_id}")

        # Создаем аренду и обновляем статус диска
        rental = await rental_repo.create_rental(user.id, available_disc.disc_id)
        logger.info(f"Аренда создана: {rental.id}")

        result = await disc_repo.update_disc_status(available_disc.disc_id, 2)  # 2 = rented
        logger.info(f"Статус диска обновлен: {result}")

        # Получаем обновленное количество доступных дисков
        available_discs_count = await disc_repo.get_available_discs_count_by_game(game_id)

        logger.info(f"Пользователь {user_id} успешно взял игру {game_id} (диск {available_disc.disc_id})")
        await callback.answer(f"✅ Вы успешно взяли игру '{game.title}'!")

        # Обновляем сообщение с актуальной информацией
        availability_text = f"✅ Вы уже взяли эту игру\n📀 Осталось дисков: {available_discs_count}"

        updated_reply = (
            f"🎮 <b>{game.title}</b>\n\n"
            f"{game.description}\n\n"
            f"{availability_text}\n\n"
            f"<code>/game_{game.id}</code>"
        )

        # Проверяем, есть ли фото в сообщении
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=updated_reply,
                parse_mode="HTML",
                reply_markup=get_game_detail_kb(game.id, False)
                # is_available = False, так как пользователь уже взял игру
            )
        else:
            await callback.message.edit_text(
                updated_reply,
                parse_mode="HTML",
                reply_markup=get_game_detail_kb(game.id, False)
            )

    except Exception as e:
        logger.error(f"Ошибка при взятии игры {game_id} пользователем {user_id}: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при взятии игры")

