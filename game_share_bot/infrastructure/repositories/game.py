from typing import Any

from sqlalchemy import select, func, case, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from game_share_bot.infrastructure.models import Game, Disc
from .base import BaseRepository
from ..models.game import GameCategory
from game_share_bot.domain.enums.disc_status import DiscStatus


class GameRepository(BaseRepository[Game]):
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

    async def get_by_id(self, game_id: int, options: Any = None) -> Game | None:
        return await super().get_by_id(
            game_id,
            options=[
                joinedload(Game.categories),
                joinedload(Game.queues),
                selectinload(Game.discs),
            ]
        )

    async def get_all_with_available_discs(self, skip: int = 0, take: int = 5) -> list[Game]:
        available_discs = (
            select(func.count(Disc.disc_id))
            .where(
                Disc.game_id == Game.id,
                Disc.status_id == DiscStatus.AVAILABLE,
            )
            .correlate(Game)
            .scalar_subquery()
        )

        stmt = (
            select(Game)
            .options(
                selectinload(Game.categories),
                selectinload(Game.discs),
            )
            .where(available_discs > 0)
            .order_by(Game.id)
            .offset(skip)
            .limit(take)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_all_with_available_discs(self) -> int:
        available_discs = (
            select(func.count(Disc.disc_id))
            .where(
                Disc.game_id == Game.id,
                Disc.status_id == DiscStatus.AVAILABLE,
            )
            .correlate(Game)
            .scalar_subquery()
        )

        stmt = select(func.count(Game.id)).where(available_discs > 0)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def search_games(self, query: str, skip: int = 0, take: int = 5) -> tuple[list[Game], int]:
        cat_match = (
            select(func.count(GameCategory.id))
            .join(Game.categories)
            .where(GameCategory.name.ilike(f"%{query}%"))
            .correlate(Game)
            .scalar_subquery()
        )

        available_discs = (
            select(func.count(Disc.disc_id))
            .where(
                Disc.game_id == Game.id,
                Disc.status_id == DiscStatus.AVAILABLE,
            )
            .correlate(Game)
            .scalar_subquery()
        )

        base_filter = (
            Game.title.ilike(f"%{query}%")
            | Game.description.ilike(f"%{query}%")
            | Game.categories.any(GameCategory.name.ilike(f"%{query}%"))
        )

        stmt = (
            select(
                Game,
                (
                    case((Game.title.ilike(f"%{query}%"), 3), else_=0)
                    + case((Game.description.ilike(f"%{query}%"), 1), else_=0)
                    + cat_match
                ).label("score")
            )
            .options(
                selectinload(Game.categories),
                selectinload(Game.discs),
            )
            .where(base_filter)
            .where(available_discs > 0)
            .order_by(text("score DESC"))
            .offset(skip)
            .limit(take)
        )

        count_stmt = (
            select(func.count(Game.id))
            .where(base_filter)
            .where(available_discs > 0)
        )

        result = await self.session.execute(stmt)
        games = result.scalars().all()

        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        return games, total_count
