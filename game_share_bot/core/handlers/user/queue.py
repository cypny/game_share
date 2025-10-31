from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import MenuCallback, RentalCallback
from game_share_bot.core.keyboards import return_kb
from game_share_bot.core.keyboards.inline.queue_page import my_queue_kb
from game_share_bot.domain.enums import MenuSection, RentalStatus
from game_share_bot.infrastructure.repositories import UserRepository, RentalRepository, DiscRepository
from game_share_bot.infrastructure.repositories.rental.queue_entry import QueueEntryRepository
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.infrastructure.utils.formatting.queue import format_my_queue

router = Router()
logger = get_logger(__name__)

@router.callback_query(MenuCallback.filter_by_section(MenuSection.QUEUE))
async def my_queue(callback: CallbackQuery, session: AsyncSession):
    user_repo = UserRepository(session)
    queue_repo = QueueEntryRepository(session)

    await callback.answer()

    user = await user_repo.get_by_tg_id(callback.from_user.id)
    if not user:
        await callback.message.edit_text("Пользователь не найден")
        return

    queues_info = await queue_repo.get_all_user_queues_full_info(user.id)

    pending_take = [rental for rental in user.rentals if rental.status_id == RentalStatus.PENDING_TAKE]

    message_text = format_my_queue(queues_info, pending_take)

    await callback.message.edit_text(
        text=message_text,
        parse_mode="HTML",
        reply_markup=my_queue_kb(pending_take),
    )


#TODO: см rented_disks.py
@router.callback_query(RentalCallback.filter(F.action == "take"))
async def take_disk(callback: CallbackQuery, callback_data: RentalCallback, session: AsyncSession):
    """Обрабатывает запрос на взятие арендованного диска"""
    user_id = callback.from_user.id
    rental_id = callback_data.rental_id

    logger.info(f"Пользователь {user_id} пытается вернуть диск по аренде {rental_id}")

    try:
        rental_repo = RentalRepository(session)

        rental = await rental_repo.get_by_id_with_relations(rental_id)
        if not rental:
            return False

        await callback.answer(f"⏳ Запрос на возврат диска '{rental.disc.game.title}' отправлен администратору!")
        await my_queue(callback, session)
        logger.info(f"Пользователь {user_id} запросил возврат диска {rental_id}")

    except Exception as e:
        logger.error(f"Ошибка при запросе возврата диска: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при запросе возврата диска")