from datetime import datetime, timezone
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from game_share_bot.scheduler.job_container import job_container
from game_share_bot.infrastructure.models.rental import Rental
from game_share_bot.infrastructure.models.rental.disc import Disc
from game_share_bot.domain.enums.rental_status import RentalStatus
from game_share_bot.infrastructure.utils import get_logger

logger = get_logger(__name__)

async def update_to_overdue():
    try:
        async with job_container.session_maker() as session:
            today = datetime.now(timezone.utc).date()

            q = (
                select(Rental)
                .options(
                    selectinload(Rental.user),
                    selectinload(Rental.disc).selectinload(Disc.game)
                )
                .where(
                    Rental.status_id == RentalStatus.ACTIVE,
                    Rental.actual_end_date.is_(None),
                    func.date(Rental.expected_end_date) < today
                )
            )

            rentals = (await session.execute(q)).scalars().all()

            if rentals:
                rental_ids = [rental.id for rental in rentals]
                await session.execute(
                    update(Rental)
                    .where(Rental.id.in_(rental_ids))
                    .values(status_id=RentalStatus.OVERDUE)
                )
                await session.commit()

            logger.info(f"Обновлено {len(rentals)} просроченных аренды.")

    except Exception as err:
        logger.error(f"Ошибка при обновлении просроченных аренды: {err}", exc_info=True)
        raise
