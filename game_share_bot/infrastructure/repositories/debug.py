import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.domain.enums.disc_status import DiscStatus as DiscStatusEnum
from game_share_bot.domain.enums.rental_status import RentalStatus as RentalStatusEnum
from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.infrastructure.models import (
    Game,
    Disc,
    DiscStatus,
    RentalStatus,
    User,
    SubscriptionPlan,
    Subscription,
)
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
        from sqlalchemy import select

        result = await self.session.execute(select(Game).limit(1))
        return result.scalar_one_or_none() is None

    async def populate_test_data(self) -> None:
        if not await self.is_database_empty():
            return

        admin_tg_id = 1710266528
        admin_user = User(
            tg_id=admin_tg_id,
            phone="admin_phone",
            name="Admin",
            role="admin",
        )
        self.session.add(admin_user)
        logger.info(f"Создан администратор с tg_id {admin_tg_id}")

        categories_data = [
            "RPG",
            "Экшен",
            "Приключения",
            "Научная фантастика",
            "Вестерн",
            "Головоломки",
            "Гонки",
            "Шутер",
            "Файтинг",
            "Стратегии",
            "Интерактивное кино",
            "Платформеры",
            "Спортивные симуляторы",
            "Кооперативные",
            "Многопользовательские",
            "Мифология",
        ]

        categories = {name: GameCategory(name=name) for name in categories_data}
        self.session.add_all(categories.values())
        await self.session.flush()

        test_games = [
            Game(
                title="The Witcher 3: Wild Hunt",
                description="Action RPG в мире фэнтези",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[
                    categories["RPG"],
                    categories["Экшен"],
                    categories["Приключения"],
                ],
            ),
            Game(
                title="Cyberpunk 2077",
                description="Научно-фантастический экшен RPG",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[
                    categories["RPG"],
                    categories["Научная фантастика"],
                    categories["Экшен"],
                ],
            ),
            Game(
                title="Red Dead Redemption 2",
                description="Приклюденческий вестерн-экшен",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[
                    categories["Приключения"],
                    categories["Экшен"],
                    categories["Вестерн"],
                ],
            ),
            Game(
                title="The Legend of Zelda: Breath of the Wild",
                description="Приклюденческая игра с открытым миром",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[
                    categories["Приключения"],
                    categories["Головоломки"],
                    categories["Экшен"],
                ],
            ),
            Game(
                title="God of War",
                description="Экшен-адвенчура в скандинавской мифологии",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[
                    categories["Экшен"],
                    categories["RPG"],
                    categories["Мифология"],
                ],
            ),
            Game(
                title="Смута",
                description="Игра года",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[
                    categories["Экшен"],
                ],
            ),
            Game(
                title="Смута 2: Месть Степана",
                description="absolute cinema",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[
                    categories["Экшен"],
                ],
            ),
            Game(
                title="Смута 3: Возвращение Савы",
                description="Эпично",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[
                    categories["Экшен"],
                ],
            ),
            Game(
                title="Клэш рояль",
                description="Описания не будет",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[
                    categories["Стратегии"],
                ],
            ),
            Game(
                title="Battelfield 6",
                description="Описания не будет",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[categories["Шутер"], categories["Многопользовательские"]],
            ),
            Game(
                title="Mortal Combat",
                description="Описания не будет",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[categories["Шутер"], categories["Многопользовательские"]],
            ),
            Game(
                title="Need for Speed",
                description="Описания не будет",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[categories["Гонки"], categories["Многопользовательские"]],
            ),
            Game(
                title="Шахматы 2",
                description="Долгожданное обновление",
                cover_image_url="https://cdn.freelance.ru/images/att/1839492_900_600.png",
                categories=[categories["Стратегии"], categories["Многопользовательские"]],
            ),
        ]
        logger.info(f"Добавлено {len(test_games)} игр")
        self.session.add_all(test_games)
        await self.session.commit()

        disc_statuses = [
            DiscStatus(id=DiscStatusEnum.AVAILABLE, status="available"),
            DiscStatus(id=DiscStatusEnum.RENTED, status="rented"),
            DiscStatus(id=DiscStatusEnum.MAINTENANCE, status="maintenance"),
            DiscStatus(id=DiscStatusEnum.PENDING_RETURN, status="pending_return"),
        ]

        rental_statuses = [
            RentalStatus(id=RentalStatusEnum.ACTIVE, status="active"),
            RentalStatus(id=RentalStatusEnum.COMPLETED, status="completed"),
            RentalStatus(id=RentalStatusEnum.OVERDUE, status="overdue"),
            RentalStatus(id=RentalStatusEnum.PENDING_RETURN, status="pending_return"),
            RentalStatus(id=RentalStatusEnum.PENDING_TAKE, status="pending_take"),
        ]
        logger.info("Добавлены статусы")
        discs = []
        for game in test_games:
            for _ in range(2):
                discs.append(
                    Disc(
                        game_id=game.id,
                        status_id=DiscStatusEnum.AVAILABLE,
                    )
                )
        logger.info("Добавлены диски игр")
        self.session.add_all(disc_statuses)
        self.session.add_all(rental_statuses)
        self.session.add_all(discs)

        plans = [
            SubscriptionPlan(
                name="Basic",
                max_simultaneous_rental=1,
                monthly_price=100,
                description="Базовый план",
            ),
            SubscriptionPlan(
                name="Premium",
                max_simultaneous_rental=3,
                monthly_price=200,
                description="Премиум план",
            ),
        ]

        self.session.add_all(plans)
        await self.session.flush()

        now = datetime.now(timezone.utc)
        admin_subscription = Subscription(
            user_id=admin_user.id,
            plan_id=plans[0].id,
            yookassa_payment_id=uuid.uuid4(),
            status=SubscriptionStatus.ACTIVE,
            start_date=now,
            end_date=now + timedelta(days=30),
            is_auto_renewal=True,
        )
        self.session.add(admin_subscription)

        await self.session.commit()
