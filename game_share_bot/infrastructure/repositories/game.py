from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.infrastructure.models import Game
from .base import BaseRepository


class GameRepository(BaseRepository[Game]):
    """
    Репозиторий для работы с моделью Game.
    """
    model = Game

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def try_create(self, title: str, description: str, image: str | None = None) -> Game | None:
        if await self.get_by_field("title", title) is not None:
            return None

        return await super().create(
            title=title,
            description=description,
            cover_image_url=image
        )
