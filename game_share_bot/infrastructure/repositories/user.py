from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.infrastructure.models import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Репозиторий для работы с моделью Game.
    """
    model = User

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def try_create(self, tg_id: int, phone: str, name: str, role: str = None) -> User | None:
        if await self.get_by_phone(phone) is not None or await self.get_by_tg_id(tg_id) is not None:
            return None

        return await super().create(
            tg_id=tg_id,
            phone=phone,
            name=name,
            role=role
        )

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        return await self.session.scalar(
            select(User).filter(User.tg_id == tg_id)
        )

    async def get_by_phone(self, phone: str) -> User | None:
        return await self.session.scalar(
            select(User).filter(User.phone == phone)
        )
