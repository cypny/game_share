from sqlalchemy import select
from sqlalchemy.orm import selectinload
from game_share_bot.scheduler.job_container import job_container
from game_share_bot.infrastructure.models.rental import Rental
from game_share_bot.infrastructure.models.rental.disc import Disc
from game_share_bot.domain.enums.rental_status import RentalStatus
from game_share_bot.infrastructure.utils import get_logger

logger = get_logger(__name__)

async def notify_overdue_rentals():
    try:
        async with job_container.session_maker() as session:
            q = (
                select(Rental)
                .options(
                    selectinload(Rental.user),
                    selectinload(Rental.disc).selectinload(Disc.game)
                )
                .where(
                    Rental.status_id == RentalStatus.OVERDUE,
                    Rental.actual_end_date.is_(None)
                )
            )

            rentals = (await session.execute(q)).scalars().all()
            bot = job_container.bot

            for rental in rentals:
                try:
                    await bot.send_message(
                        chat_id=rental.user.tg_id,
                        text=f"Ваша аренда диска {rental.disc.game.title} просрочена. Пожалуйста, верните его как можно скорее."
                    )
                except Exception as e:
                    logger.error(f"Не удалось отправить сообщение пользователю {rental.user.tg_id}: {e}")

            logger.info(f"Отправлено уведомлений о просроченной аренде: {len(rentals)}")

    except Exception as err:
        logger.error(f"Ошибка при уведомлении о просроченной аренде: {err}", exc_info=True)
        raise
