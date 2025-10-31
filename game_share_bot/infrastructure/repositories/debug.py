from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from game_share_bot.domain.enums.disc_status import DiscStatus as DiscStatusEnum
from game_share_bot.domain.enums.rental_status import RentalStatus as RentalStatusEnum
from game_share_bot.infrastructure.models import Game, Disc, DiscStatus, RentalStatus, User, SubscriptionPlan
from game_share_bot.infrastructure.models.game import GameCategory
from game_share_bot.infrastructure.utils.logging import get_logger

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
        categories_data = [
            "RPG", "Экшен", "Приключения", "Научная фантастика",
            "Вестерн", "Головоломка", "Мифология"
        ]

        categories = {name: GameCategory(name=name) for name in categories_data}
        self.session.add_all(categories.values())
        await self.session.flush()  # Чтобы получить ID категорий

        # Затем создаем игры
        test_games = [
            Game(
                title="The Witcher 3: Wild Hunt",
                description="Action RPG в мире фэнтези",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[categories["RPG"], categories["Экшен"], categories["Приключения"]]
            ),
            Game(
                title="Cyberpunk 2077",
                description="Научно-фантастический экшен RPG",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[categories["RPG"], categories["Научная фантастика"], categories["Экшен"]]
            ),
            Game(
                title="Red Dead Redemption 2",
                description="Приклюденческий вестерн-экшен",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[categories["Приключения"], categories["Экшен"], categories["Вестерн"]]
            ),
            Game(
                title="The Legend of Zelda: Breath of the Wild",
                description="Приклюденческая игра с открытым миром",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[categories["Приключения"], categories["Головоломка"], categories["Экшен"]]
            ),
            Game(
                title="God of War",
                description="Экшен-адвенчура в скандинавской мифологии",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[categories["Экшен"], categories["RPG"], categories["Мифология"]]
            )
        ]
        logger.info(f"Добавлено {len(test_games)} игр")
        self.session.add_all(test_games)
        await self.session.commit()

        disc_statuses = [
            DiscStatus(id=DiscStatusEnum.AVAILABLE, status="available"),
            DiscStatus(id=DiscStatusEnum.RENTED, status="rented"),
            DiscStatus(id=DiscStatusEnum.MAINTENANCE, status="maintenance"),
            DiscStatus(id=DiscStatusEnum.PENDING_RETURN, status="pending_return")
        ]

        rental_statuses = [
            RentalStatus(id=RentalStatusEnum.ACTIVE, status="active"),
            RentalStatus(id=RentalStatusEnum.COMPLETED, status="completed"),
            RentalStatus(id=RentalStatusEnum.OVERDUE, status="overdue"),
            RentalStatus(id=RentalStatusEnum.PENDING_RETURN, status="pending_return"),
            RentalStatus(id=RentalStatusEnum.PENDING_TAKE, status="pending_take"),
        ]
        logger.info(f"Добавлены статусы")
        discs = []
        for game in test_games:
            for i in range(2):  # по 2 диска на игру
                discs.append(Disc(
                    game_id=game.id,
                    status_id=DiscStatusEnum.AVAILABLE
                ))
        logger.info(f"Добавлены диски игр")
        self.session.add_all(disc_statuses)
        self.session.add_all(rental_statuses)
        self.session.add_all(discs)

        # Планы подписок
        plans = [
            SubscriptionPlan(name="Basic", max_simultaneous_rental=1, monthly_price=100,
                             description="Базовый план"),
            SubscriptionPlan(name="Premium", max_simultaneous_rental=3, monthly_price=200,
                             description="Премиум план")
        ]

        self.session.add_all(plans)


        await self.session.commit()