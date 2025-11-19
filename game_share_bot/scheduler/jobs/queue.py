from sqlalchemy import func, select, text
from sqlalchemy.orm import selectinload

from game_share_bot.domain.enums import DiscStatus, RentalStatus
from game_share_bot.infrastructure.models import QueueEntry, Disc, Rental, User
from game_share_bot.scheduler.job_container import job_container

#TODO
async def update_queue_to_rental():
    async with job_container.session_maker() as session:

        queue_rn_col = func.row_number().over(
            partition_by=QueueEntry.game_id,
            order_by=QueueEntry.created_at
        ).label("queue_rn")

        queue_subq = (
            select(
                QueueEntry.id.label("entry_id"),
                QueueEntry.game_id
            )
            .where(QueueEntry.is_active.is_(True))
            .add_columns(queue_rn_col)
            .subquery()
        )

        disc_rn_col = func.row_number().over(
            partition_by=Disc.game_id,
            order_by=Disc.disc_id
        ).label("disc_rn")

        disc_subq = (
            select(
                Disc.disc_id.label("disc_id"),
                Disc.game_id
            )
            .where(Disc.status_id == DiscStatus.AVAILABLE)
            .add_columns(disc_rn_col)
            .subquery()
        )

        stmt = (
            select(QueueEntry, Disc)
            .join(queue_subq, queue_subq.c.entry_id == QueueEntry.id)
            .join(disc_subq, (
                    (disc_subq.c.game_id == queue_subq.c.game_id) &
                    (disc_subq.c.disc_rn == 1)
            ))
            .join(Disc, Disc.disc_id == disc_subq.c.disc_id)
            .where(queue_subq.c.queue_rn == 1)
            .options(selectinload(QueueEntry.user).selectinload(User.rentals).selectinload(Rental.disc))
            .with_for_update(of=[QueueEntry, Disc])
        )

        result = await session.execute(stmt)
        rows = result.all()

        if not rows:
            return

        rentals_to_add = []

        for queue_entry, disc in rows:
            queue_entry.is_active = False
            disc.status_id = DiscStatus.RENTED
            has_active_rental_for_this_game = False

            for rental in queue_entry.user.rentals:
                if rental.disc.game_id == disc.game_id:
                    has_active_rental_for_this_game = True
                    break
            if has_active_rental_for_this_game:
                continue
            # TODO: с полями разобраться
            new_rental = Rental(
                user_id=queue_entry.user_id,
                disc_id=disc.disc_id,
                status_id=RentalStatus.PENDING_TAKE
            )
            rentals_to_add.append(new_rental)

        session.add_all(rentals_to_add)

        try:
            await session.commit()
        except Exception:
            await session.execute(text("SELECT setval('rentals_id_seq', (SELECT MAX(id) FROM rentals))"))
            await session.rollback()
            raise
