from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from sqlalchemy.orm import joinedload

from game_share_bot.infrastructure.models import Subscription
from .base import BaseRepository
from game_share_bot.infrastructure.models import User


class SubscriptionRepository(BaseRepository[Subscription]):
    model = Subscription

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user(self, user: User) -> Subscription:
        return await super().get_by_field(
            "user_id",
            user.id,
            options=[joinedload(Subscription.plan)])