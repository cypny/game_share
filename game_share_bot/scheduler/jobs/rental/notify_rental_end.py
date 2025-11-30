from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from game_share_bot.infrastructure.models import Disc
from game_share_bot.infrastructure.models.rental import Rental
from game_share_bot.domain.enums.rental_status import RentalStatus
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.scheduler.job_container import job_container

logger = get_logger(__name__)

async def notify_rental_end():
    try:
        async with job_container.session_maker() as session:
            today = datetime.now(timezone.utc).date()
            tomorrow = today + timedelta(days=1)

            allowed_statuses = [RentalStatus.ACTIVE]

            base_query = (
                select(Rental)
                .options(
                    selectinload(Rental.user),
                    selectinload(Rental.disc).selectinload(Disc.game)
                )
                .where(
                    Rental.status_id.in_(allowed_statuses),
                    Rental.actual_end_date.is_(None)
                )
            )

            q_tomorrow = base_query.where(func.date(Rental.expected_end_date) == tomorrow)
            rentals_tomorrow = (await session.execute(q_tomorrow)).scalars().all()

            q_today = base_query.where(func.date(Rental.expected_end_date) == today)
            rentals_today = (await session.execute(q_today)).scalars().all()

            bot = job_container.bot

            for rental in rentals_tomorrow:
                await bot.send_message(
                    chat_id=rental.user.tg_id,
                    text=f"Напоминаем: аренда диска {rental.disc.game.title} заканчивается завтра."
                )

            for rental in rentals_today:
                await bot.send_message(
                    chat_id=rental.user.tg_id,
                    text=f"Сегодня срок сдачи диска {rental.disc.game.title}. Пожалуйста, верните его."
                )

    except Exception as err:
        logger.error(err, exc_info=True)
        raise
