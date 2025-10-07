from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from game_share_bot.infrastructure.models import Rental
from .base import BaseRepository

class RentalRepository(BaseRepository[Rental]):
    model = Rental

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_rental(self, user_id: int, disc_id: int) -> Rental:
        """Создать запись о аренде"""
        rental_data = {
            "user_id": user_id,
            "disc_id": disc_id,
            "status_id": 1,  # 1 = active
            "start_date": datetime.now(),
            "expected_end_date": datetime.now() + timedelta(days=7),
            "actual_end_date": None
        }
        return await self.create(**rental_data)
