from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.infrastructure.models.game import GameCategory

from .base import BaseRepository


class GameCategoryRepository(BaseRepository[GameCategory]):
    model = GameCategory

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_name(self, name: str) -> GameCategory:
        return await super().get_by_field("name", name)
