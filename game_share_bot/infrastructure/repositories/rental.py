from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from game_share_bot.infrastructure.models import Rental, Disc, User, Game
from .base import BaseRepository


class RentalRepository(BaseRepository[Rental]):
    """Репозиторий для операций с арендой игровых дисков"""
    model = Rental

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_rental(self, user_id: int, disc_id: int) -> Rental:
        """Создает новую запись об аренде диска"""
        rental_data = {
            "user_id": user_id,
            "disc_id": disc_id,
            "status_id": 1,
            "start_date": datetime.now(),
            "expected_end_date": datetime.now() + timedelta(days=7),
            "actual_end_date": None
        }
        return await self.create(**rental_data)

    async def get_active_rental_by_user_and_game(self, user_id: int, game_id: int) -> Rental | None:
        """Находит активную аренду пользователя для конкретной игры"""
        stmt = (
            select(Rental)
            .join(Disc, Rental.disc_id == Disc.disc_id)
            .options(selectinload(Rental.disc))
            .where(
                Rental.user_id == user_id,
                Disc.game_id == game_id,
                Rental.status_id == 1
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_rentals_by_user(self, tg_id: int) -> list[Rental]:
        """Возвращает все активные аренды пользователя по telegram ID с загрузкой связанных данных"""
        stmt = (
            select(Rental)
            .join(User, Rental.user_id == User.id)
            .join(Disc, Rental.disc_id == Disc.disc_id)
            .join(Game, Disc.game_id == Game.id)
            .options(
                selectinload(Rental.user),
                selectinload(Rental.disc).selectinload(Disc.game)
            )
            .where(
                User.tg_id == tg_id,
                Rental.status_id == 1
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_with_relations(self, rental_id: int) -> Rental | None:
        """Получает аренду по ID с загрузкой связанных объектов"""
        stmt = (
            select(Rental)
            .options(
                selectinload(Rental.user),
                selectinload(Rental.disc).selectinload(Disc.game)
            )
            .where(Rental.id == rental_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_disc(self, rental_id: int) -> Rental | None:
        """Получает аренду по ID с загрузкой только диска (для операций возврата)"""
        stmt = (
            select(Rental)
            .options(selectinload(Rental.disc))
            .where(Rental.id == rental_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_rental_status(self, rental_id: int, status_id: int) -> bool:
        """Обновляет статус аренды и устанавливает дату возврата"""
        rental = await self.get_by_id_with_disc(rental_id)
        if not rental:
            return False

        rental.status_id = status_id
        if status_id == 2:
            rental.actual_end_date = datetime.now()

        await self.session.commit()
        return True