# game_share_bot/infrastructure/repositories/disc.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from game_share_bot.infrastructure.models import Disc
from .base import BaseRepository

class DiscRepository(BaseRepository[Disc]):
    model = Disc

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_available_disc_by_game(self, game_id: int) -> Disc | None:
        """Получить первый доступный диск для игры"""
        stmt = select(Disc).where(
            Disc.game_id == game_id,
            Disc.status_id == 1  # 1 = available
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_disc_status(self, disc_id: int, status_id: int) -> bool:
        """Обновить статус диска"""
        result = await self.update(disc_id, status_id=status_id)
        return result is not None
