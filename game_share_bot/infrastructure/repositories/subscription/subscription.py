from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.infrastructure.models import Subscription, User
from game_share_bot.infrastructure.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    model = Subscription

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_all_by_user(self, user: User) -> list[Subscription]:
        return await super().get_all_by_field("user_id", user.id, options=[joinedload(Subscription.plan)])

    async def get_active_by_user(self, user: User) -> Subscription | None:
        stmt = select(Subscription).where(
            Subscription.status == SubscriptionStatus.ACTIVE, Subscription.user_id == user.id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_with_status(self, status: SubscriptionStatus):
        return await super().get_all_by_field(
            "status",
            status,
            options=[joinedload(Subscription.plan), joinedload(Subscription.user)],
        )

    async def get_all_pending(self) -> list[Subscription]:
        return await self.get_all_with_status(SubscriptionStatus.PENDING_PAYMENT)

    async def get_all_active(self) -> list[Subscription]:
        return await self.get_all_with_status(SubscriptionStatus.ACTIVE)
