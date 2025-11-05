from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import GameCallback
from game_share_bot.domain.enums import RentalStatus
from game_share_bot.domain.enums.actions.game_actions import GameAction
from game_share_bot.domain.rental.queue import get_entry_position
from game_share_bot.infrastructure.models import User
from game_share_bot.infrastructure.repositories.rental.queue_entry import QueueEntryRepository
from game_share_bot.infrastructure.utils.formatting import format_game_full
from game_share_bot.core.keyboards import enter_queue_kb
from game_share_bot.infrastructure.repositories import GameRepository, DiscRepository, RentalRepository, UserRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)

#TODO: отрефакторить это чудо
@router.message(F.text.startswith("/game_"))
async def cmd_game(message: Message, session: AsyncSession):
    tg_id = message.from_user.id
    logger.info(f"Пользователь {tg_id} запросил информацию об игре: {message.text}")

    try:
        game_repo = GameRepository(session)
        disc_repo = DiscRepository(session)
        user_repo = UserRepository(session)

        game_id = int(message.text.split('_')[1])
        logger.debug(f"Поиск игры с ID: {game_id}")

        game = await game_repo.get_by_id(game_id)
        if game is None:
            logger.warning(f"Игра {game_id} не найдена для пользователя {tg_id}")
            await message.answer("Игра не найдена")
            return

        user = await user_repo.get_by_tg_id(tg_id)
        available_discs_count = await disc_repo.get_available_discs_count_by_game(game_id)

        game = await game_repo.get_by_id(game_id)
        queue_entries = game.queues
        queue_position = get_entry_position(user.id, queue_entries)
        has_rental_this_game = [
            r for r in user.rentals
            if r.disc.game_id == game_id and r.status_id != RentalStatus.COMPLETED
        ]

        is_available = (available_discs_count > 0 and
                        queue_position is None and
                        not has_rental_this_game)

        availability_text = "Вы можете встать в очередь"
        if available_discs_count <= 0:
            availability_text = "Нет свободных дисков"
        if queue_position is not None:
            availability_text = "Вы уже стоите в этой очереди"
        if has_rental_this_game:
            availability_text = "Вы уже арендовали эту игру"


        reply = format_game_full(game, available_discs_count, queue_position, availability_text)

        if game.cover_image_url:
            await message.answer_photo(
                photo=game.cover_image_url,
                caption=reply,
                parse_mode="HTML",
                reply_markup=enter_queue_kb(game.id, is_available)
            )
        else:
            await message.answer(
                reply,
                parse_mode="HTML",
                reply_markup=enter_queue_kb(game.id, is_available)
            )

        logger.info(f"Информация об игре {game_id} отправлена пользователю {tg_id}")
    except Exception as e:
        logger.error(f"Ошибка при получении информации об игре для пользователя {tg_id}: {str(e)}", exc_info=True)
        await message.answer("❌ Ошибка при загрузке информации об игре")

@router.callback_query(GameCallback.filter_by_action(GameAction.REQUEST_QUEUE))
async def enter_game_queue(callback: CallbackQuery, callback_data: GameCallback, session: AsyncSession):
    """Обработчик кнопки 'Взять игру' на странице игры"""
    tg_id = callback.from_user.id
    game_id = callback_data.game_id

    logger.info(f"Пользователь {tg_id} пытается взять игру {game_id}")

    try:
        game_repo = GameRepository(session)
        disc_repo = DiscRepository(session)
        user_repo = UserRepository(session)
        queue_repo = QueueEntryRepository(session)

        user = await user_repo.get_by_tg_id(tg_id)
        if not user:
            await callback.answer("❌ Сначала нужно зарегистрироваться")
            return

        message = await _can_enter_queue(user)
        if message:
            await callback.answer(message)
            return

        existing_active_queue_entry = next(
            (entry for entry in user.queues
                 if entry.game_id == game_id and entry.is_active),
            None
        )
        if existing_active_queue_entry:
            await callback.answer("❌ Вы уже стоите в очереди за этой игрой")
            return

        available_disc = await disc_repo.get_available_disc_by_game(game_id)

        if not available_disc:
            await callback.answer("❌ Все диски этой игры заняты")
            return

        game = await game_repo.get_by_id(game_id)
        if not game:
            await callback.answer("❌ Игра не найдена")
            return

        new_entry = await queue_repo.create_queue_entry(user.id, game_id)
        logger.info(f"{new_entry}")
        # result = await disc_repo.update_disc_status(available_disc.disc_id, DiscStatus.RENTED)
        available_discs_count = await disc_repo.get_available_discs_count_by_game(game_id)

        await callback.answer(f"✅ Вы успешно взяли игру '{game.title}'!")

        entries = game.queues
        queue_position = get_entry_position(user.id, entries)

        has_rental_this_game = [
            r for r in user.rentals
            if r.disc.game_id == game_id and r.status_id != RentalStatus.COMPLETED
        ]

        is_available = (available_discs_count > 0 and
                        queue_position is None and
                        not has_rental_this_game)

        availability_text = "Вы уже стоите в этой очереди"

        updated_reply = format_game_full(game, available_discs_count, queue_position, availability_text)

        if callback.message.photo:
            await callback.message.edit_caption(
                caption=updated_reply,
                parse_mode="HTML",
                reply_markup=enter_queue_kb(game.id, False)
                # is_available = False, так как пользователь уже взял игру
            )
        else:
            await callback.message.edit_text(
                updated_reply,
                parse_mode="HTML",
                reply_markup=enter_queue_kb(game.id, False)
            )

    except Exception as e:
        logger.error(f"Ошибка при взятии игры {game_id} пользователем {tg_id}: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при взятии игры")

async def _can_enter_queue(user: User) -> str:
    if not user.subscription:
        return "У вас нет подписки"
    sub_plan = user.subscription.plan
    if len([r for r in user.rentals if r.status_id != RentalStatus.COMPLETED]) >= sub_plan.max_simultaneous_rental:
        return f"Исчерпан лимит дисков ({len(user.rentals)}) для подписки {sub_plan.name}"

    return None
