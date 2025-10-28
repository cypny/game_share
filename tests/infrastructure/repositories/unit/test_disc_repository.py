import pytest
from game_share_bot.infrastructure.repositories.rental.disc import DiscRepository
from game_share_bot.infrastructure.repositories.game import GameRepository
from game_share_bot.domain.enums import DiscStatus


class TestDiscRepository:
    @pytest.mark.asyncio
    async def test_create_disc(self, test_session):
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

        assert disc is not None
        assert disc.disc_id == 1
        assert disc.game_id == game.id
        assert disc.status_id == DiscStatus.AVAILABLE

    @pytest.mark.asyncio
    async def test_get_available_disc_by_game(self, test_session):
        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        disc_repo = DiscRepository(test_session)
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

        found_disc = await disc_repo.get_available_disc_by_game(game.id)
        assert found_disc is not None
        assert found_disc.disc_id == 1
        assert found_disc.status_id == DiscStatus.AVAILABLE

    @pytest.mark.asyncio
    async def test_get_available_disc_by_game_none_available(self, test_session):
        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        disc_repo = DiscRepository(test_session)
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

        found_disc = await disc_repo.get_available_disc_by_game(game.id)
        assert found_disc is None

    @pytest.mark.asyncio
    async def test_get_available_discs_count_by_game(self, test_session):
        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        disc_repo = DiscRepository(test_session)
        await disc_repo.create(disc_id=1, game_id=game.id, status_id=DiscStatus.AVAILABLE)
        await disc_repo.create(disc_id=2, game_id=game.id, status_id=DiscStatus.AVAILABLE)
        await disc_repo.create(disc_id=3, game_id=game.id, status_id=DiscStatus.RENTED)
        await disc_repo.create(disc_id=4, game_id=game.id, status_id=DiscStatus.MAINTENANCE)

        count = await disc_repo.get_available_discs_count_by_game(game.id)
        assert count == 2

    @pytest.mark.asyncio
    async def test_update_disc_status(self, test_session):
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

        result = await disc_repo.update_disc_status(
            disc.disc_id,
            DiscStatus.RENTED
        )

        assert result is True
        updated_disc = await disc_repo.get_by_id(disc.disc_id)
        assert updated_disc.status_id == DiscStatus.RENTED

    @pytest.mark.asyncio
    async def test_get_discs_by_game(self, test_session):
        game_repo = GameRepository(test_session)
        game = await game_repo.create(
            title="Test Game",
            description="Test Description"
        )

        disc_repo = DiscRepository(test_session)
        await disc_repo.create(disc_id=1, game_id=game.id, status_id=DiscStatus.AVAILABLE)
        await disc_repo.create(disc_id=2, game_id=game.id, status_id=DiscStatus.RENTED)

        discs = await disc_repo.get_all_by_field("game_id", game.id)
        assert len(discs) == 2
        assert all(disc.game_id == game.id for disc in discs)