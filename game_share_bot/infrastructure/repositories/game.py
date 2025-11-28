from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from game_share_bot.infrastructure.models import Game, GameCategory

from .base import BaseRepository


class GameRepository(BaseRepository[Game]):
    model = Game

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def try_create(
        self, title: str, description: str, categories: list[GameCategory], image: str | None = None
    ) -> Game | None:
        if await self.get_by_field("title", title) is not None:
            return None

        return await super().create(title=title,
                                    description=description,
                                    categories=categories,
                                    cover_image_url=image)

    async def get_by_id(self, game_id: int, options=None) -> Game | None:
        return await super().get_by_id(game_id, options=[joinedload(Game.categories), joinedload(Game.queues)])

    async def search_games(self, query: str, skip=0, take=5) -> tuple[list[Game], int]:
        stmt = (
            select(Game)
            .order_by(func.levenshtein(Game.title, query))
            .offset(skip)
            .limit(take)
        )

        result = await self.session.execute(stmt)
        games = result.scalars().all()

        count_stmt = select(func.count()).select_from(self.model)
        count = await self.session.scalar(count_stmt)

        return games, count

    async def get_by_category(self, category_id: int, skip: int = 0, take: int = 10) -> tuple[list[Game], int]:
        stmt = (
            select(Game)
            .join(Game.categories)
            .where(GameCategory.id == category_id)
            .order_by(Game.title)
            .offset(skip)
            .limit(take)
        )

        result = await self.session.execute(stmt)
        games = result.scalars().all()

        count_stmt = (
            select(func.count())
            .select_from(
                select(Game.id)
                .join(Game.categories)
                .where(GameCategory.id == category_id)
                .subquery()
            )
        )
        count = await self.session.scalar(count_stmt)

        return games, count
