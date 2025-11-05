import uuid
from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from game_share_bot.domain.enums import DiscStatus
from game_share_bot.infrastructure.models import QueueEntry, Disc, Game
from game_share_bot.infrastructure.repositories.base import BaseRepository

from dataclasses import dataclass

@dataclass
class QueueFullInfo:
    queue_entry: QueueEntry
    position: int
    total_in_queue: int
    game: "Game"

class QueueEntryRepository(BaseRepository[QueueEntry]):
    model = QueueEntry

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_queue_entry(self, user_id: uuid.UUID, disc_id: int) -> QueueEntry:
        """Создает новую запись об аренде диска"""
        queue_entry_data = {
            "user_id": user_id,
            "game_id": disc_id
        }
        queue_entry = await self.create(**queue_entry_data)
        return queue_entry


    async def get_all_user_queues_full_info(self, user_id: uuid.UUID) -> List[QueueFullInfo]:
        position_col = func.row_number().over(
            partition_by=QueueEntry.game_id,
            order_by=QueueEntry.created_at
        ).label("position")

        total_in_queue_col = func.count(QueueEntry.id).over(
            partition_by=QueueEntry.game_id
        ).label("total_in_queue")

        subq = (
            select(
                QueueEntry.id.label("entry_id"),
                QueueEntry.user_id,
                position_col,
                total_in_queue_col
            )
            .where(QueueEntry.is_active.is_(True))
            .subquery()
        )

        stmt = (
            select(
                QueueEntry,
                subq.c.position.label("position"),
                subq.c.total_in_queue.label("total_in_queue"),
            )
            .join(subq, subq.c.entry_id == QueueEntry.id)
            .where(subq.c.user_id == user_id)
            .options(selectinload(QueueEntry.game))
        )

        result = await self.session.execute(stmt)
        rows = result.mappings().all()  # теперь строки — dict-подобные объекты

        infos: List[QueueFullInfo] = [
            QueueFullInfo(
                queue_entry=row["QueueEntry"],
                position=row["position"],
                total_in_queue=row["total_in_queue"],
                game=row["QueueEntry"].game
            )
            for row in rows
        ]

        return infos

    async def get_queue_position(self, queue_entry: QueueEntry) -> int:
        query = select(func.count(QueueEntry.id)).where(
            QueueEntry.game_id == queue_entry.game_id,
            QueueEntry.is_active == True,
            QueueEntry.created_at < queue_entry.created_at
        )

        result = await self.session.scalar(query)
        position = (result or 0) + 1  # +1 потому что позиция начинается с 1

        return position


