from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.domain.enums import DiscStatus
from game_share_bot.infrastructure.models import Disc
from game_share_bot.infrastructure.repositories.base import BaseRepository


class DiscRepository(BaseRepository[Disc]):
    model = Disc

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def add_disc(self, game_id: int) -> Disc | None:
        """Добавить диск для игры по id"""
        return await super().create(
            game_id=game_id,
            status_id=DiscStatus.AVAILABLE
        )

    async def try_delete_disc(self, game_id: int) -> bool:
        disc_to_delete = await self.get_available_disc_by_game(game_id)
        if disc_to_delete is None:
            return False
        return await super().delete(disc_to_delete.disc_id)

    async def get_available_disc_by_game(self, game_id: int) -> Disc | None:
        """Получить первый доступный диск для игры"""
        stmt = select(Disc).where(
            Disc.game_id == game_id,
            Disc.status_id == DiscStatus.AVAILABLE
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_disc_count_by_game(self, game_id: int) -> int:
        """Получить общее количество дисков для игры"""
        stmt = select(func.count(Disc.disc_id)).where(Disc.game_id == game_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_available_discs_count_by_game(self, game_id: int) -> int:
        """Получить количество доступных дисков для игры"""
        stmt = select(func.count(Disc.disc_id)).where(
            Disc.game_id == game_id,
            Disc.status_id == DiscStatus.AVAILABLE
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update_disc_status(self, disc_id: int, status: DiscStatus) -> bool:
        stmt = select(Disc).where(Disc.disc_id == disc_id)
        result = await self.session.execute(stmt)
        disc = result.scalar_one_or_none()

        if disc:
            disc.status_id = status
            await self.session.flush()
            return True
        return False
