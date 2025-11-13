from typing import Any

from sqlalchemy import select, func, desc, case, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from game_share_bot.infrastructure.models import Game
from .base import BaseRepository
from ..models.game import GameCategory


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

    async def get_by_id(self, game_id:int, options = None) -> Game | None:
        return await super().get_by_id(game_id, options = [joinedload(Game.categories), joinedload(Game.queues)])

    async def search_games(self, query: str, skip=0, take=5) ->  tuple[list[Game], int]:
        """Возвращает найденные игры и их общее количество"""
        stmt = (
            select(Game)
            # .where(func.levenshtein(Game.title, query) <= 3)
            .order_by(func.levenshtein(Game.title, query))
            .offset(skip)
            .limit(take)
        )
        result = await self.session.execute(stmt)
        games = result.scalars().all()

        count_stmt = select(func.count()).select_from(self.model)
        count =  await self.session.scalar(count_stmt)

        return games, count
