import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestGameCommands:
    @pytest.mark.asyncio
    async def test_cmd_game_success_with_photo(self, mock_message, test_session):
        with patch('game_share_bot.core.handlers.games.catalog.GameRepository') as mock_game_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.DiscRepository') as mock_disc_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.RentalRepository') as mock_rental_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.UserRepository') as mock_user_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.get_game_detail_kb') as mock_kb:
            mock_game_repo = AsyncMock()
            mock_disc_repo = AsyncMock()
            mock_rental_repo = AsyncMock()
            mock_user_repo = AsyncMock()

            mock_game_repo_class.return_value = mock_game_repo
            mock_disc_repo_class.return_value = mock_disc_repo
            mock_rental_repo_class.return_value = mock_rental_repo
            mock_user_repo_class.return_value = mock_user_repo

            test_game = MagicMock(
                id=1,
                title="Test Game",
                description="Test Description",
                cover_image_url="https://example.com/cover.jpg"
            )
            mock_game_repo.get_by_id.return_value = test_game

            test_user = MagicMock(id=1)
            mock_user_repo.get_by_tg_id.return_value = test_user

            mock_disc_repo.get_available_discs_count_by_game.return_value = 3
            mock_rental_repo.get_active_rental_by_user_and_game.return_value = None

            mock_kb.return_value = "mock_game_keyboard"

            mock_message.text = "/game_1"

            from game_share_bot.core.handlers.games.catalog import cmd_game
            await cmd_game(mock_message, test_session)

            mock_game_repo.get_by_id.assert_called_with(1)
            mock_user_repo.get_by_tg_id.assert_called_with(mock_message.from_user.id)
            mock_disc_repo.get_available_discs_count_by_game.assert_called_with(1)
            mock_rental_repo.get_active_rental_by_user_and_game.assert_called_with(1, 1)

            mock_message.answer_photo.assert_called_once()
            call_args = mock_message.answer_photo.call_args
            assert call_args[1]['photo'] == "https://example.com/cover.jpg"
            assert "Test Game" in call_args[1]['caption']
            assert "Доступно дисков: 3" in call_args[1]['caption']
            assert call_args[1]['reply_markup'] == "mock_game_keyboard"

    @pytest.mark.asyncio
    async def test_cmd_game_user_has_active_rental(self, mock_message, test_session):
        with patch('game_share_bot.core.handlers.games.catalog.GameRepository') as mock_game_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.DiscRepository') as mock_disc_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.RentalRepository') as mock_rental_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.UserRepository') as mock_user_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.get_game_detail_kb') as mock_kb:
            mock_game_repo = AsyncMock()
            mock_disc_repo = AsyncMock()
            mock_rental_repo = AsyncMock()
            mock_user_repo = AsyncMock()

            mock_game_repo_class.return_value = mock_game_repo
            mock_disc_repo_class.return_value = mock_disc_repo
            mock_rental_repo_class.return_value = mock_rental_repo
            mock_user_repo_class.return_value = mock_user_repo

            test_game = MagicMock(
                id=1,
                title="Test Game",
                description="Test Description",
                cover_image_url=None
            )
            mock_game_repo.get_by_id.return_value = test_game

            test_user = MagicMock(id=1)
            mock_user_repo.get_by_tg_id.return_value = test_user

            mock_rental_repo.get_active_rental_by_user_and_game.return_value = MagicMock()
            mock_disc_repo.get_available_discs_count_by_game.return_value = 2

            mock_kb.return_value = "mock_game_keyboard"

            mock_message.text = "/game_1"

            from game_share_bot.core.handlers.games.catalog import cmd_game
            await cmd_game(mock_message, test_session)

            mock_kb.assert_called_with(1, False)

            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args
            assert "Вы уже взяли эту игру" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_cmd_game_not_found(self, mock_message, test_session):
        with patch('game_share_bot.core.handlers.games.catalog.GameRepository') as mock_game_repo_class:
            mock_game_repo = AsyncMock()
            mock_game_repo_class.return_value = mock_game_repo
            mock_game_repo.get_by_id.return_value = None

            mock_message.text = "/game_999"

            from game_share_bot.core.handlers.games.catalog import cmd_game
            await cmd_game(mock_message, test_session)

            mock_message.answer.assert_called_with("Игра не найдена")

    @pytest.mark.asyncio
    async def test_cmd_game_invalid_format(self, mock_message, test_session):
        mock_message.text = "/game_invalid"

        from game_share_bot.core.handlers.games.catalog import cmd_game
        await cmd_game(mock_message, test_session)

        mock_message.answer.assert_called_with("❌ Неверный формат команды. Используйте: /game_1")

    @pytest.mark.asyncio
    async def test_cmd_game_user_not_registered(self, mock_message, test_session):
        with patch('game_share_bot.core.handlers.games.catalog.GameRepository') as mock_game_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.UserRepository') as mock_user_repo_class:
            mock_game_repo = AsyncMock()
            mock_user_repo = AsyncMock()

            mock_game_repo_class.return_value = mock_game_repo
            mock_user_repo_class.return_value = mock_user_repo

            test_game = MagicMock(id=1, title="Test Game", description="Test Description")
            mock_game_repo.get_by_id.return_value = test_game
            mock_user_repo.get_by_tg_id.return_value = None

            mock_message.text = "/game_1"

            from game_share_bot.core.handlers.games.catalog import cmd_game
            await cmd_game(mock_message, test_session)

            mock_message.answer_photo.assert_called_once()
            call_args = mock_message.answer_photo.call_args
            assert "Test Game" in call_args[1]['caption']