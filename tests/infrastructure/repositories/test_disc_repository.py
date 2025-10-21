import pytest
from game_share_bot.infrastructure.repositories.rental.disc import DiscRepository
from game_share_bot.infrastructure.repositories.game import GameRepository
from game_share_bot.infrastructure.models.game import Game
from game_share_bot.infrastructure.models.rental.disc import Disc
from game_share_bot.domain.enums import DiscStatus


class TestDiscRepository:
    """Тесты для DiscRepository с реальной БД"""

    @pytest.mark.asyncio
    async def test_create_disc(self, test_session):
        """Тест создания диска"""
        # Сначала создаем игру
        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        # Создаем диск
        disc_repo = DiscRepository(test_session)
        disc = await disc_repo.create(
            disc_id=1,  # Явно задаем disc_id
            game_id=game.id,
            status_id=DiscStatus.AVAILABLE
        )

        assert disc is not None
        assert disc.disc_id == 1
        assert disc.game_id == game.id
        assert disc.status_id == DiscStatus.AVAILABLE

    @pytest.mark.asyncio
    async def test_get_available_disc_by_game(self, test_session):
        """Тест поиска доступного диска по игре"""
        # Создаем игру
        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        disc_repo = DiscRepository(test_session)

        # Создаем несколько дисков с разными статусами
        available_disc = await disc_repo.create(
            disc_id=1,
            game_id=game.id,
            status_id=DiscStatus.AVAILABLE
        )
        await disc_repo.create(
            disc_id=2,
            game_id=game.id,
            status_id=DiscStatus.RENTED
        )

        # Ищем доступный диск
        found_disc = await disc_repo.get_available_disc_by_game(game.id)

        assert found_disc is not None
        assert found_disc.disc_id == 1
        assert found_disc.status_id == DiscStatus.AVAILABLE

    @pytest.mark.asyncio
    async def test_get_available_disc_by_game_none_available(self, test_session):
        """Тест поиска доступного диска, когда нет доступных"""
        # Создаем игру
        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        disc_repo = DiscRepository(test_session)

        # Создаем только занятые диски
        await disc_repo.create(
            disc_id=1,
            game_id=game.id,
            status_id=DiscStatus.RENTED
        )
        await disc_repo.create(
            disc_id=2,
            game_id=game.id,
            status_id=DiscStatus.RENTED
        )

        # Ищем доступный диск
        found_disc = await disc_repo.get_available_disc_by_game(game.id)

        assert found_disc is None

    @pytest.mark.asyncio
    async def test_get_available_discs_count_by_game(self, test_session):
        """Тест подсчета доступных дисков по игре"""
        # Создаем игру
        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        disc_repo = DiscRepository(test_session)

        # Создаем диски с разными статусами
        await disc_repo.create(disc_id=1, game_id=game.id, status_id=DiscStatus.AVAILABLE)
        await disc_repo.create(disc_id=2, game_id=game.id, status_id=DiscStatus.AVAILABLE)
        await disc_repo.create(disc_id=3, game_id=game.id, status_id=DiscStatus.RENTED)
        await disc_repo.create(disc_id=4, game_id=game.id, status_id=DiscStatus.MAINTENANCE)

        # Получаем количество доступных дисков
        count = await disc_repo.get_available_discs_count_by_game(game.id)

        assert count == 2

    @pytest.mark.asyncio
    async def test_update_disc_status(self, test_session):
        """Тест обновления статуса диска"""
        # Создаем игру и диск
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

        # Обновляем статус
        result = await disc_repo.update_disc_status(
            disc.disc_id,
            DiscStatus.RENTED
        )

        assert result is True

        # Проверяем, что статус обновился
        updated_disc = await disc_repo.get_by_id(disc.disc_id)
        assert updated_disc.status_id == DiscStatus.RENTED

    @pytest.mark.asyncio
    async def test_get_discs_by_game(self, test_session):
        """Тест получения всех дисков по игре"""
        # Создаем игру
        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        disc_repo = DiscRepository(test_session)

        # Создаем диски для этой игры
        await disc_repo.create(disc_id=1, game_id=game.id, status_id=DiscStatus.AVAILABLE)
        await disc_repo.create(disc_id=2, game_id=game.id, status_id=DiscStatus.RENTED)

        # Получаем диски только для первой игры используя существующий метод
        discs = await disc_repo.get_all_by_field("game_id", game.id)

        assert len(discs) == 2
        assert all(disc.game_id == game.id for disc in discs)