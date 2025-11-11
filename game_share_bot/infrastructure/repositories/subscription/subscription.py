import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from game_share_bot.infrastructure.models import Subscription
from game_share_bot.infrastructure.models import User
from game_share_bot.infrastructure.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    model = Subscription

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_all_by_user(self, user: User) ->  list[Subscription]:
        return await super().get_all_by_field(
            "user_id",
            user.id,
            options=[joinedload(Subscription.plan)])