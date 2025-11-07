from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from game_share_bot.infrastructure.models import User, Subscription, Rental, Disc
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
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
        return await self.get_by_field(
            "tg_id",
            tg_id,
            options=[
                selectinload(User.subscription).selectinload(Subscription.plan),
                selectinload(User.rentals).selectinload(Rental.disc).selectinload(Disc.game),
                selectinload(User.queues)
            ])

    async def get_by_phone(self, phone: str) -> User | None:
        return await self.get_by_field("phone", phone)

    async def get_by_role(self, role: str) -> User | None:
        return await self.get_by_field("role", role)

    async def make_admin(self, tg_id: int) -> bool:
        """Выдает права администратора пользователю"""
        user = await self.get_by_tg_id(tg_id)
        if user is None:
            return False

        user.role = "admin"
        await self.session.flush()
        return True

    async def get_all_admins(self) -> list[User]:
        """Возвращает список всех администраторов"""
        from sqlalchemy import select
        stmt = select(User).where(User.role == "admin")
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
