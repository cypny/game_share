import pytest
from datetime import datetime, timedelta
from game_share_bot.infrastructure.repositories.user import UserRepository
from game_share_bot.infrastructure.repositories.game import GameRepository
from game_share_bot.infrastructure.repositories.rental.disc import DiscRepository
from game_share_bot.infrastructure.repositories.rental.rental import RentalRepository
from game_share_bot.domain.enums import DiscStatus, RentalStatus


class TestRentalIntegration:
    """Интеграционные тесты для полного цикла аренды"""

    @pytest.mark.asyncio
    async def test_complete_rental_flow(self, test_session):
        """Тест полного цикла аренды: пользователь берет и возвращает игру"""
        # Фиксированное время для тестов (без временной зоны)
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)

        # 1. Создаем пользователя
        user_repo = UserRepository(test_session)
        user = await user_repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="Test User"
        )

        # 2. Создаем игру
        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="The Witcher 3",
            description="RPG Game",
            cover_image_url="witcher.jpg"
        )

        # 3. Создаем доступные диски
        disc_repo = DiscRepository(test_session)
        disc1 = await disc_repo.create(disc_id=1, game_id=game.id, status_id=DiscStatus.AVAILABLE)
        disc2 = await disc_repo.create(disc_id=2, game_id=game.id, status_id=DiscStatus.AVAILABLE)

        # Проверяем начальное состояние
        available_count = await disc_repo.get_available_discs_count_by_game(game.id)
        assert available_count == 2

        # 4. Пользователь берет игру (создаем аренду)
        rental_repo = RentalRepository(test_session)

        # Создаем аренду вручную с фиксированным временем
        rental = await rental_repo.create(
            user_id=user.id,
            disc_id=disc1.disc_id,
            status_id=RentalStatus.ACTIVE,
            start_date=fixed_time,
            expected_end_date=fixed_time + timedelta(days=30),
            actual_end_date=None
        )

        # 5. Обновляем статус диска на "арендован"
        await disc_repo.update_disc_status(disc1.disc_id, DiscStatus.RENTED)

        # Проверяем состояние после взятия
        available_count_after_rent = await disc_repo.get_available_discs_count_by_game(game.id)
        assert available_count_after_rent == 1

        active_rentals = await rental_repo.get_active_rentals_by_user(user.tg_id)
        assert len(active_rentals) == 1
        assert active_rentals[0].id == rental.id

        # Проверяем статус диска
        rented_disc = await disc_repo.get_by_id(disc1.disc_id)
        assert rented_disc.status_id == DiscStatus.RENTED

        # 6. Пользователь возвращает игру
        await rental_repo.update_rental_status(rental.id, RentalStatus.COMPLETED)
        await disc_repo.update_disc_status(disc1.disc_id, DiscStatus.AVAILABLE)

        # Проверяем состояние после возврата
        available_count_after_return = await disc_repo.get_available_discs_count_by_game(game.id)
        assert available_count_after_return == 2

        completed_rental = await rental_repo.get_by_id(rental.id)
        assert completed_rental.status_id == RentalStatus.COMPLETED
        assert completed_rental.actual_end_date is not None

        returned_disc = await disc_repo.get_by_id(disc1.disc_id)
        assert returned_disc.status_id == DiscStatus.AVAILABLE

        # У пользователя не должно быть активных аренд
        active_rentals_after_return = await rental_repo.get_active_rentals_by_user(user.tg_id)
        assert len(active_rentals_after_return) == 0

    @pytest.mark.asyncio
    async def test_multiple_users_rent_same_game(self, test_session):
        """Тест когда несколько пользователей арендуют одну игру"""
        # Фиксированное время для тестов (без временной зоны)
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)

        # Создаем пользователей
        user_repo = UserRepository(test_session)
        user1 = await user_repo.try_create(tg_id=111, phone="+1111111111", name="User 1")
        user2 = await user_repo.try_create(tg_id=222, phone="+2222222222", name="User 2")

        # Создаем игру с двумя дисками
        game_repo = GameRepository(test_session)
        game = await game_repo.create(title="Popular Game", description="Very popular")

        disc_repo = DiscRepository(test_session)
        disc1 = await disc_repo.create(disc_id=1, game_id=game.id, status_id=DiscStatus.AVAILABLE)
        disc2 = await disc_repo.create(disc_id=2, game_id=game.id, status_id=DiscStatus.AVAILABLE)

        # Оба пользователя берут игру
        rental_repo = RentalRepository(test_session)

        # Создаем аренды с фиксированным временем
        rental1 = await rental_repo.create(
            user_id=user1.id,
            disc_id=disc1.disc_id,
            status_id=RentalStatus.ACTIVE,
            start_date=fixed_time,
            expected_end_date=fixed_time + timedelta(days=30),
            actual_end_date=None
        )
        rental2 = await rental_repo.create(
            user_id=user2.id,
            disc_id=disc2.disc_id,
            status_id=RentalStatus.ACTIVE,
            start_date=fixed_time,
            expected_end_date=fixed_time + timedelta(days=30),
            actual_end_date=None
        )

        # Обновляем статусы дисков
        await disc_repo.update_disc_status(disc1.disc_id, DiscStatus.RENTED)
        await disc_repo.update_disc_status(disc2.disc_id, DiscStatus.RENTED)

        # Проверяем, что дисков больше нет в наличии
        available_count = await disc_repo.get_available_discs_count_by_game(game.id)
        assert available_count == 0

        # Проверяем активные аренды
        user1_rentals = await rental_repo.get_active_rentals_by_user(user1.tg_id)
        user2_rentals = await rental_repo.get_active_rentals_by_user(user2.tg_id)

        assert len(user1_rentals) == 1
        assert len(user2_rentals) == 1
        assert user1_rentals[0].id == rental1.id
        assert user2_rentals[0].id == rental2.id