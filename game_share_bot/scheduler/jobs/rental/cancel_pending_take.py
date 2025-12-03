from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from game_share_bot.domain.enums import DiscStatus
from game_share_bot.scheduler.job_container import job_container
from game_share_bot.infrastructure.models.rental import Rental
from game_share_bot.infrastructure.models.rental.disc import Disc
from game_share_bot.domain.enums.rental_status import RentalStatus
from game_share_bot.infrastructure.utils import get_logger

logger = get_logger(__name__)


async def cancel_pending_take():
    try:
        async with job_container.session_maker() as session:
            time_threshold = datetime.now(timezone.utc) - timedelta(days=1)

            q = (
                select(Rental)
                .options(
                    selectinload(Rental.user),
                    selectinload(Rental.disc).selectinload(Disc.game)
                )
                .where(
                    Rental.status_id == RentalStatus.PENDING_TAKE,
                    Rental.created_at < time_threshold
                )
            )

            rentals = (await session.execute(q)).scalars().all()

            if rentals:
                rental_ids = [rental.id for rental in rentals]
                disc_ids = [rental.disc_id for rental in rentals]

                # Обновляем статус аренд на отмененный
                await session.execute(
                    update(Rental)
                    .where(Rental.id.in_(rental_ids))
                    .values(status_id=RentalStatus.CANCELED)
                )

                # Освобождаем диски
                await session.execute(
                    update(Disc)
                    .where(Disc.disc_id.in_(disc_ids))
                    .values(status_id=DiscStatus.AVAILABLE)
                )

                await session.commit()

            logger.info(f"Отменено {len(rentals)} аренд и освобождено {len(disc_ids)} дисков.")

            logger.info(f"Отменено {len(rentals)} аренд со статусом 'ожидает взятия'.")

    except Exception as err:
        logger.error(f"Ошибка при отмене аренд: {err}", exc_info=True)
        raise
