from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.infrastructure.models import Game, Disc, DiscStatus, RentalStatus, User
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.domain.enums.rental_status import RentalStatus
from game_share_bot.domain.enums.disc_status import DiscStatus
logger = get_logger(__name__)


class DebugRepository:
    """
    Репозиторий для дебага и тестовых данных.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_database_empty(self) -> bool:
        """Проверяет, пустая ли БД (нет игр)."""
        from sqlalchemy import select
        result = await self.session.execute(select(Game).limit(1))
        return result.scalar_one_or_none() is None

    async def populate_test_data(self) -> None:
        """Добавляет тестовые данные если БД пустая."""
        if not await self.is_database_empty():
            return

        # Добавляем тестового администратора
        admin_tg_id = 1710266528
        admin_user = User(
            tg_id=admin_tg_id,
            phone="admin_phone",
            name="Admin",
            role="admin"
        )
        self.session.add(admin_user)
        logger.info(f"Создан администратор с tg_id {admin_tg_id}")

        # Добавляем тестовые игры
        test_games = [
            Game(
                title="The Witcher 3: Wild Hunt",
                description="Action RPG в мире фэнтези",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png"
            ),
            Game(
                title="Cyberpunk 2077",
                description="Научно-фантастический экшен RPG",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png"
            ),
            Game(
                title="Red Dead Redemption 2",
                description="Приклюденческий вестерн-экшен",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png"
            ),
            Game(
                title="The Legend of Zelda: Breath of the Wild",
                description="Приклюденческая игра с открытым миром",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png"
            ),
            Game(
                title="God of War",
                description="Экшен-адвенчура в скандинавской мифологии",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png"
            )
        ]
        logger.info(f"Добавлено {len(test_games)} игр")
        self.session.add_all(test_games)
        await self.session.commit()

        disc_statuses = [
            DiscStatus(id=DiscStatus.AVAILABLE, status="available"),
            DiscStatus(id=DiscStatus.RENTED, status="rented"),
            DiscStatus(id=DiscStatus.MAINTENANCE, status="maintenance"),
            DiscStatus(id=DiscStatus.PENDING_RETURN, status="pending_return")
        ]

        rental_statuses = [
            RentalStatus(id=RentalStatus.ACTIVE, status="active"),
            RentalStatus(id=RentalStatus.COMPLETED, status="completed"),
            RentalStatus(id=RentalStatus.OVERDUE, status="overdue"),
            RentalStatus(id=RentalStatus.PENDING_RETURN, status="pending_return")
        ]
        logger.info(f"Добавлены статусы")
        discs = []
        disc_id = 1
        for game in test_games:
            for i in range(2):  # по 2 диска на игру
                discs.append(Disc(
                    disc_id=disc_id,
                    game_id=game.id,
                    status_id=DiscStatus.AVAILABLE
                ))
                disc_id += 1
        logger.info(f"Добавлены диски игр")
        self.session.add_all(disc_statuses)
        self.session.add_all(rental_statuses)
        self.session.add_all(discs)
        await self.session.commit()