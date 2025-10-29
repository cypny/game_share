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
        return await super().get_by_id(game_id, options = [joinedload(Game.categories)])

    async def search_games(self, query: str, skip=0, take=5) ->  tuple[list[Game], int]:
        """Возвращает найденные игры и их общее количество"""
        cat_match = (
            select(func.count(GameCategory.id))
            .join(Game.categories)
            .where(GameCategory.name.ilike(f"%{query}%"))
            .correlate(Game)
            .scalar_subquery()
        )

        stmt = (
            select(
                Game,
                (
                        case((Game.title.ilike(f"%{query}%"), 3), else_=0) +
                        case((Game.description.ilike(f"%{query}%"), 1), else_=0) +
                        cat_match
                ).label("score")
            )
            .options(selectinload(Game.categories))
            .where(
                Game.title.ilike(f"%{query}%")
                | Game.description.ilike(f"%{query}%")
                | Game.categories.any(GameCategory.name.ilike(f"%{query}%"))
            )
            .order_by(text("score DESC"))
            .order_by()
            .offset(skip)
            .limit(take)
        )

        count_stmt = (
            select(func.count(Game.id))
            .where(
                Game.title.ilike(f"%{query}%")
                | Game.description.ilike(f"%{query}%")
                | Game.categories.any(GameCategory.name.ilike(f"%{query}%"))
            )
        )

        result = await self.session.execute(stmt)
        count_result = await self.session.execute(count_stmt)

        games = result.scalars().all()
        total_count = count_result.scalar()

        return games, total_count
