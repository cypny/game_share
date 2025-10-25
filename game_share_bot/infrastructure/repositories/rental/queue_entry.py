import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from game_share_bot.infrastructure.models import QueueEntry, Disc
from game_share_bot.infrastructure.repositories.base import BaseRepository


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
        return await self.create(**queue_entry_data)

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
