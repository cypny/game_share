import pytest
from datetime import datetime, timedelta
from game_share_bot.infrastructure.repositories.rental.rental import RentalRepository
from game_share_bot.infrastructure.repositories.user import UserRepository
from game_share_bot.infrastructure.repositories.game import GameRepository
from game_share_bot.infrastructure.repositories.rental.disc import DiscRepository
from game_share_bot.infrastructure.models.rental.rental import Rental
from game_share_bot.domain.enums import DiscStatus, RentalStatus


class TestRentalRepository:
    """Тесты для RentalRepository с реальной БД"""

    @pytest.mark.asyncio
    async def test_create_rental_success(self, test_session):
        """Тест успешного создания аренды"""
        # Фиксированное время для тестов (без временной зоны)
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)

        # Создаем пользователя, игру и диск
        user_repo = UserRepository(test_session)
        user = await user_repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="Test User"
        )

        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        disc_repo = DiscRepository(test_session)
        disc = await disc_repo.create(
            disc_id=1,  # Явно задаем disc_id
            game_id=game.id,
            status_id=DiscStatus.AVAILABLE
        )

        # Создаем аренду с фиксированным временем
        rental_repo = RentalRepository(test_session)
        rental = await rental_repo.create(
            user_id=user.id,
            disc_id=disc.disc_id,
            status_id=RentalStatus.ACTIVE,
            start_date=fixed_time,
            expected_end_date=fixed_time + timedelta(days=30),
            actual_end_date=None
        )

        assert rental is not None
        assert rental.id is not None
        assert rental.user_id == user.id
        assert rental.disc_id == disc.disc_id
        assert rental.status_id == RentalStatus.ACTIVE

        # При сравнении времени игнорируем микросекунды, так как БД может их обрезать
        assert rental.start_date.replace(microsecond=0) == fixed_time
        assert rental.expected_end_date.replace(microsecond=0) == fixed_time + timedelta(days=30)

        # Проверяем, что аренда сохранена в БД
        saved_rental = await rental_repo.get_by_id(rental.id)
        assert saved_rental is not None

    @pytest.mark.asyncio
    async def test_get_active_rental_by_user_and_game(self, test_session):
        """Тест поиска активной аренды по пользователю и игре"""
        # Фиксированное время для тестов (без временной зоны)
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)

        # Создаем пользователя, игру и диск
        user_repo = UserRepository(test_session)
        user = await user_repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="Test User"
        )

        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        disc_repo = DiscRepository(test_session)
        disc = await disc_repo.create(
            disc_id=1,  # Явно задаем disc_id
            game_id=game.id,
            status_id=DiscStatus.AVAILABLE
        )

        # Создаем активную аренду
        rental_repo = RentalRepository(test_session)
        rental = await rental_repo.create(
            user_id=user.id,
            disc_id=disc.disc_id,
            status_id=RentalStatus.ACTIVE,
            start_date=fixed_time,
            expected_end_date=fixed_time + timedelta(days=30),
            actual_end_date=None
        )

        # Ищем активную аренду
        found_rental = await rental_repo.get_active_rental_by_user_and_game(
            user.id, game.id
        )

        assert found_rental is not None
        assert found_rental.id == rental.id
        assert found_rental.status_id == RentalStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_get_active_rental_by_user_and_game_not_found(self, test_session):
        """Тест поиска активной аренды, когда ее нет"""
        user_repo = UserRepository(test_session)
        user = await user_repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="Test User"
        )

        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        rental_repo = RentalRepository(test_session)
        found_rental = await rental_repo.get_active_rental_by_user_and_game(
            user.id, game.id
        )

        assert found_rental is None

    @pytest.mark.asyncio
    async def test_get_active_rentals_by_user(self, test_session):
        """Тест получения всех активных аренд пользователя"""
        # Фиксированное время для тестов (без временной зоны)
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)

        user_repo = UserRepository(test_session)
        user = await user_repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="Test User"
        )

        game_repo = GameRepository(test_session)
        game1 = await game_repo.create(title="Game 1", description="Desc 1")
        game2 = await game_repo.create(title="Game 2", description="Desc 2")

        disc_repo = DiscRepository(test_session)
        disc1 = await disc_repo.create(disc_id=1, game_id=game1.id, status_id=DiscStatus.AVAILABLE)
        disc2 = await disc_repo.create(disc_id=2, game_id=game2.id, status_id=DiscStatus.AVAILABLE)

        # Создаем активные аренды
        rental_repo = RentalRepository(test_session)
        rental1 = await rental_repo.create(
            user_id=user.id,
            disc_id=disc1.disc_id,
            status_id=RentalStatus.ACTIVE,
            start_date=fixed_time,
            expected_end_date=fixed_time + timedelta(days=30),
            actual_end_date=None
        )
        rental2 = await rental_repo.create(
            user_id=user.id,
            disc_id=disc2.disc_id,
            status_id=RentalStatus.ACTIVE,
            start_date=fixed_time,
            expected_end_date=fixed_time + timedelta(days=30),
            actual_end_date=None
        )

        # Получаем активные аренды пользователя
        active_rentals = await rental_repo.get_active_rentals_by_user(user.tg_id)

        assert len(active_rentals) == 2
        assert any(rental.id == rental1.id for rental in active_rentals)
        assert any(rental.id == rental2.id for rental in active_rentals)
        assert all(rental.status_id == RentalStatus.ACTIVE for rental in active_rentals)

    @pytest.mark.asyncio
    async def test_complete_rental(self, test_session):
        """Тест завершения аренды"""
        # Фиксированное время для тестов (без временной зоны)
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)

        user_repo = UserRepository(test_session)
        user = await user_repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="Test User"
        )

        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        disc_repo = DiscRepository(test_session)
        disc = await disc_repo.create(
            disc_id=1,  # Явно задаем disc_id
            game_id=game.id,
            status_id=DiscStatus.AVAILABLE
        )

        # Создаем аренду
        rental_repo = RentalRepository(test_session)
        rental = await rental_repo.create(
            user_id=user.id,
            disc_id=disc.disc_id,
            status_id=RentalStatus.ACTIVE,
            start_date=fixed_time,
            expected_end_date=fixed_time + timedelta(days=30),
            actual_end_date=None
        )

        # Завершаем аренду используя существующий метод
        result = await rental_repo.update_rental_status(rental.id, RentalStatus.COMPLETED)

        assert result is True

        # Проверяем, что аренда завершена
        completed_rental = await rental_repo.get_by_id(rental.id)
        assert completed_rental.status_id == RentalStatus.COMPLETED
        assert completed_rental.actual_end_date is not None

    @pytest.mark.asyncio
    async def test_get_rental_with_details(self, test_session):
        """Тест получения аренды с деталями (пользователь, диск, игра)"""
        # Фиксированное время для тестов (без временной зоны)
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)

        user_repo = UserRepository(test_session)
        user = await user_repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="Test User"
        )

        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        disc_repo = DiscRepository(test_session)
        disc = await disc_repo.create(
            disc_id=1,
            game_id=game.id,
            status_id=DiscStatus.AVAILABLE
        )

        # Создаем аренду
        rental_repo = RentalRepository(test_session)
        rental = await rental_repo.create(
            user_id=user.id,
            disc_id=disc.disc_id,
            status_id=RentalStatus.ACTIVE,
            start_date=fixed_time,
            expected_end_date=fixed_time + timedelta(days=30),
            actual_end_date=None
        )

        # Получаем аренду с деталями используя существующий метод
        rental_with_details = await rental_repo.get_by_id_with_relations(rental.id)

        assert rental_with_details is not None
        assert rental_with_details.id == rental.id
        assert rental_with_details.user.id == user.id
        assert rental_with_details.disc.disc_id == disc.disc_id
        assert rental_with_details.disc.game.id == game.id