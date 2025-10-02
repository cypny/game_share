from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.repositories import UserRepository


class IsAdmin(Filter):
    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_tg_id(message.from_user.id)

        return user and user.role == 'admin'