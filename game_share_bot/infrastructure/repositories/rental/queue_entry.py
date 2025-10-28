import uuid
from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from game_share_bot.domain.enums import DiscStatus
from game_share_bot.infrastructure.models import QueueEntry, Disc
from game_share_bot.infrastructure.repositories.base import BaseRepository

from dataclasses import dataclass

@dataclass
class QueueFullInfo:
    queue_entry: QueueEntry
    position: int
    total_in_queue: int
    game: "Game"
    disc: Disc

class QueueEntryRepository(BaseRepository[QueueEntry]):
    model = QueueEntry

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_queue_entry(self, user_id: uuid.UUID, disc_id: int) -> QueueEntry:
        """Создает новую запись об аренде диска"""
        queue_entry_data = {
            "user_id": user_id,
            "disc_id": disc_id
        }
        queue_entry = await self.create(**queue_entry_data)

        # Меняем статус диска на "в очереди" или "забронирован"
        disc = await self.session.get(Disc, disc_id)
        if disc:
            disc.status_id = DiscStatus.AVAILABLE  # или другой подходящий статус

        return queue_entry

    async def get_active_user_queue_entries_for_game(
            self,
            user_id: uuid.UUID,
            game_id: int
    ) -> QueueEntry:
        stmt = (
            select(QueueEntry)
            .join(QueueEntry.disc)
            .options(joinedload(QueueEntry.user), joinedload(QueueEntry.disc))
            .where(
                QueueEntry.user_id == user_id,
                Disc.game_id == game_id,
                QueueEntry.is_active == True
            )
            .order_by(QueueEntry.created_at)
        )

        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_queue_entries_for_game(self, game_id: uuid.UUID) -> List[QueueEntry]:
        """Возвращает позиции в порядке возрастания дат (на нулевом индексе первый получит диск)"""
        stmt = (
            select(QueueEntry)
            .join(QueueEntry.disc)
            .options(
                joinedload(QueueEntry.user),
                joinedload(QueueEntry.disc).joinedload(Disc.game),
                joinedload(QueueEntry.disc).joinedload(Disc.status)
            )
            .where(
                Disc.game_id == game_id,
                QueueEntry.is_active == True
            )
            .order_by(QueueEntry.created_at)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_user_queues_full_info(self, user_id: uuid.UUID) -> List[QueueFullInfo]:
        position_expr = func.row_number().over(
            partition_by=QueueEntry.disc_id,
            order_by=QueueEntry.created_at
        ).label("position")

        total_expr = func.count().over(
            partition_by=QueueEntry.disc_id
        ).label("total_in_queue")

        query = (
            select(
                QueueEntry,
                position_expr,
                total_expr
            )
            .where(QueueEntry.is_active == True)
            .options(
                joinedload(QueueEntry.disc).joinedload(Disc.game)
            )
            .order_by(QueueEntry.disc_id, QueueEntry.created_at)
        )

        result = await self.session.execute(query)
        rows = result.all()
        filtered_rows = [
            row for row in rows
            if row[0].user_id == user_id
        ]

        return [
            QueueFullInfo(
                queue_entry=row[0],
                position=row[1],
                total_in_queue=row[2],
                game=row[0].disc.game,
                disc=row[0].disc
            )
            for row in filtered_rows
        ]

    async def get_queue_position(self, queue_entry: QueueEntry) -> int:
        query = select(func.count(QueueEntry.id)).where(
            QueueEntry.disc_id == queue_entry.disc_id,
            QueueEntry.is_active == True,
            QueueEntry.created_at < queue_entry.created_at
        )

        result = await self.session.scalar(query)
        position = (result or 0) + 1  # +1 потому что позиция начинается с 1

        return position


