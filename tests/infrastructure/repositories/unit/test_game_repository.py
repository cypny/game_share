import pytest
from game_share_bot.infrastructure.repositories.game import GameRepository


class TestGameRepository:
    @pytest.mark.asyncio
    async def test_create_game_success(self, test_session):
        repo = GameRepository(test_session)
        game = await repo.create(
            title="Test Game",
            description="Test Description",
            cover_image_url="https://example.com/cover.jpg"
        )
        assert game is not None
        assert game.id is not None
        assert game.title == "Test Game"
        assert game.description == "Test Description"
        assert game.cover_image_url == "https://example.com/cover.jpg"

        saved_game = await repo.get_by_id(game.id)
        assert saved_game is not None
        assert saved_game.title == "Test Game"

    @pytest.mark.asyncio
    async def test_try_create_duplicate_title(self, test_session):
        repo = GameRepository(test_session)
        game1 = await repo.try_create(
            title="Duplicate Game",
            description="Description 1",
            image="image1.jpg"
        )
        assert game1 is not None

        game2 = await repo.try_create(
            title="Duplicate Game",
            description="Description 2",
            image="image2.jpg"
        )
        assert game2 is None

    @pytest.mark.asyncio
    async def test_get_all_games(self, test_session):
        repo = GameRepository(test_session)
        await repo.create(title="Game 1", description="Desc 1")
        await repo.create(title="Game 2", description="Desc 2")
        await repo.create(title="Game 3", description="Desc 3")

        games = await repo.get_all()
        assert len(games) == 3
        assert any(game.title == "Game 1" for game in games)
        assert any(game.title == "Game 2" for game in games)
        assert any(game.title == "Game 3" for game in games)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, test_session):
        repo = GameRepository(test_session)
        game = await repo.get_by_id(999)
        assert game is None

    @pytest.mark.asyncio
    async def test_update_game(self, test_session):
        repo = GameRepository(test_session)
        game = await repo.create(
            title="Original Title",
            description="Original Description",
            cover_image_url="original.jpg"
        )

        updated_game = await repo.update(
            game.id,
            title="Updated Title",
            description="Updated Description"
        )

        assert updated_game is not None
        assert updated_game.title == "Updated Title"
        assert updated_game.description == "Updated Description"
        assert updated_game.cover_image_url == "original.jpg"

        saved_game = await repo.get_by_id(game.id)
        assert saved_game.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_delete_game(self, test_session):
        repo = GameRepository(test_session)
        game = await repo.create(
            title="Game to Delete",
            description="Will be deleted"
        )

        result = await repo.delete(game.id)
        assert result is True

        deleted_game = await repo.get_by_id(game.id)
        assert deleted_game is None