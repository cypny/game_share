from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import MenuCallback
from game_share_bot.core.keyboards import return_kb
from game_share_bot.domain.enums import MenuSection, RentalStatus
from game_share_bot.infrastructure.repositories import UserRepository
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

    pending_take = filter(
            lambda r: r.status_id == RentalStatus.PENDING_TAKE,
            user.rentals)

    message_text = format_my_queue(queues_info, pending_take)

    await callback.message.edit_text(
        text=message_text,
        parse_mode="HTML",
        reply_markup=return_kb(MenuCallback(section=MenuSection.PERSONAL_CABINET)),
    )