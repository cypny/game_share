from dataclasses import dataclass

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import GameCallback
from game_share_bot.core.keyboards import enter_queue_kb, take_disc_confirmation_kb
from game_share_bot.core.states import TakeDiscState
from game_share_bot.domain.enums import RentalStatus
from game_share_bot.domain.enums.actions.game_actions import GameAction
from game_share_bot.domain.rental.queue import get_entry_position
from game_share_bot.infrastructure.models import User, Game
from game_share_bot.infrastructure.repositories.rental.queue_entry import QueueEntryRepository
from game_share_bot.infrastructure.utils.formatting import format_game_full
from game_share_bot.infrastructure.repositories import GameRepository, DiscRepository, RentalRepository, UserRepository
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.scheduler.jobs.queue import update_queue_to_rental_internal

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

        game_status_info = await _get_game_status_info(user, game, session)

        reply = format_game_full(game, game_status_info)

        if game.cover_image_url:
            await message.answer_photo(
                photo=game.cover_image_url,
                caption=reply,
                parse_mode="HTML",
                reply_markup=enter_queue_kb(game.id, game_status_info.can_enter_queue)
            )
        else:
            await message.answer(
                reply,
                parse_mode="HTML",
                reply_markup=enter_queue_kb(game.id, game_status_info.can_enter_queue)
            )

        logger.info(f"Информация об игре {game_id} отправлена пользователю {tg_id}")
    except Exception as e:
        logger.error(f"Ошибка при получении информации об игре для пользователя {tg_id}: {str(e)}", exc_info=True)
        await message.answer("❌ Ошибка при загрузке информации об игре")

@router.callback_query(GameCallback.filter_by_action(GameAction.REQUEST_QUEUE))
async def enter_game_queue(callback: CallbackQuery, callback_data: GameCallback, session: AsyncSession, state: FSMContext):
    """Обработчик кнопки 'Взять игру' на странице игры"""
    tg_id = callback.from_user.id
    game_id = callback_data.game_id

    logger.info(f"Пользователь {tg_id} пытается взять игру {game_id}")

    try:
        game_repo = GameRepository(session)
        disc_repo = DiscRepository(session)
        user_repo = UserRepository(session)
        queue_repo = QueueEntryRepository(session)
        rental_repo = RentalRepository(session)

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

        await session.flush()
        await update_queue_to_rental_internal(session)
        await session.flush()
        await session.refresh(user)

        logger.info(f"{new_entry}")

        # Проверяем, был ли создан rental со статусом PENDING_TAKE
        pending_rental = next(
            (rental for rental in user.rentals
             if rental.disc.game_id == game_id and rental.status_id == RentalStatus.PENDING_TAKE),
            None
        )

        # Если создан rental (пользователь первый в очереди) - показываем окно подтверждения
        if pending_rental:
            logger.info(f"Пользователь {tg_id} стал первым в очереди, показываем окно подтверждения для rental {pending_rental.id}")

            await state.update_data(rental_id=pending_rental.id)
            await state.set_state(TakeDiscState.waiting_for_confirmation)

            await callback.answer("✅ Диск готов к получению!")
            await callback.message.answer(
                f"🎮 <b>{game.title}</b>\n\n"
                f"❓ Вы точно взяли диск?\n\n"
                f"⚠️ Пожалуйста, подтвердите только после того, как физически забрали диск.",
                parse_mode="HTML",
                reply_markup=take_disc_confirmation_kb(pending_rental.id)
            )
        else:
            # Пользователь встал в очередь, но не первый
            await callback.answer(f"✅ Вы успешно встали в очередь за игрой '{game.title}'!")

        game_status_info = await _get_game_status_info(user, game, session)
        updated_reply = format_game_full(game, game_status_info)

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
        raise

@dataclass
class GameStatusInfo:
    available_discs_count: int
    queue_position: int | None
    has_active_rental: bool
    availability_status: str
    queue_status: str
    can_enter_queue: bool

async def _can_enter_queue(user: User) -> str | None:
    if not user.subscription:
        return "У вас нет подписки"
    sub_plan = user.subscription.plan
    if len([r for r in user.rentals if r.status_id != RentalStatus.COMPLETED]) >= sub_plan.max_simultaneous_rental:
        return f"Исчерпан лимит дисков ({len(user.rentals)}) для подписки {sub_plan.name}"

    return None

async def _get_game_status_info(user: User, game: Game, session: AsyncSession) -> GameStatusInfo:
    disc_repo = DiscRepository(session)

    available_discs_count = await disc_repo.get_available_discs_count_by_game(game.id)
    queue_position = get_entry_position(user.id, game.queues)

    has_active_rental = any(
        r for r in user.rentals
        if r.disc.game_id == game.id and r.status_id != RentalStatus.COMPLETED
    )

    # Определяем статусы
    availability_status = _get_availability_status(available_discs_count)
    queue_status = _get_queue_status(queue_position, has_active_rental, available_discs_count)

    # Определяем можно ли встать в очередь
    can_enter_queue = (
            available_discs_count > 0 and
            queue_position is None and
            not has_active_rental and
            await _can_enter_queue(user) is None  # Проверка подписки и лимитов
    )

    return GameStatusInfo(
        available_discs_count=available_discs_count,
        queue_position=queue_position,
        has_active_rental=has_active_rental,
        availability_status=availability_status,
        queue_status=queue_status,
        can_enter_queue=can_enter_queue
    )

def _get_availability_status(available_discs_count: int) -> str:
    if available_discs_count > 0:
        return f"✅ Доступно дисков: {available_discs_count}"
    return "❌ Все диски заняты"

def _get_queue_status(queue_position: int | None, has_active_rental: bool, available_discs_count: int) -> str:
    if has_active_rental:
        return "📦 У вас уже арендована эта игра"
    if queue_position is not None:
        return f"🎯 Ваша позиция в очереди: {queue_position}"
    if available_discs_count > 0:
        return "⏳ Вы можете встать в очередь"
    return ""


