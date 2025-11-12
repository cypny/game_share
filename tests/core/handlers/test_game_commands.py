import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestGameCommands:
    @pytest.mark.asyncio
    async def test_cmd_game_success_with_photo(self, mock_message, test_session):
        with patch("game_share_bot.core.handlers.games.game.GameRepository") as mock_game_repo_class, \
             patch("game_share_bot.core.handlers.games.game.DiscRepository") as mock_disc_repo_class, \
             patch("game_share_bot.core.handlers.games.game.UserRepository") as mock_user_repo_class, \
             patch("game_share_bot.core.handlers.games.game.get_entry_position") as mock_get_pos, \
             patch("game_share_bot.core.handlers.games.game.format_game_full") as mock_format, \
             patch("game_share_bot.core.handlers.games.game.enter_queue_kb") as mock_kb:

            mock_game_repo = AsyncMock()
            mock_disc_repo = AsyncMock()
            mock_user_repo = AsyncMock()
            mock_game_repo_class.return_value = mock_game_repo
            mock_disc_repo_class.return_value = mock_disc_repo
            mock_user_repo_class.return_value = mock_user_repo

            game = MagicMock(
                id=1,
                title="Test Game",
                description="Desc",
                cover_image_url="https://example.com/cover.jpg",
                queues=[],
            )
            user = MagicMock(id=10, rentals=[], queues=[])
            mock_game_repo.get_by_id.return_value = game
            mock_user_repo.get_by_tg_id.return_value = user
            mock_disc_repo.get_available_discs_count_by_game.return_value = 2
            mock_get_pos.return_value = None
            mock_format.return_value = "FULL_INFO"
            mock_kb.return_value = "KB"

            mock_message.text = "/game_1"

            from game_share_bot.core.handlers.games.game import cmd_game
            await cmd_game(mock_message, test_session)

            mock_game_repo.get_by_id.assert_awaited()
            mock_user_repo.get_by_tg_id.assert_awaited()
            mock_disc_repo.get_available_discs_count_by_game.assert_awaited()
            assert mock_kb.called

            mock_message.answer_photo.assert_called_once()
            call = mock_message.answer_photo.call_args
            assert call.kwargs["photo"] == "https://example.com/cover.jpg"
            assert call.kwargs["caption"] == "FULL_INFO"
            assert call.kwargs.get("parse_mode") == "HTML"
            assert call.kwargs["reply_markup"] == "KB"

    @pytest.mark.asyncio
    async def test_cmd_game_success_without_photo(self, mock_message, test_session):
        with patch("game_share_bot.core.handlers.games.game.GameRepository") as mock_game_repo_class, \
             patch("game_share_bot.core.handlers.games.game.DiscRepository") as mock_disc_repo_class, \
             patch("game_share_bot.core.handlers.games.game.UserRepository") as mock_user_repo_class, \
             patch("game_share_bot.core.handlers.games.game.get_entry_position") as mock_get_pos, \
             patch("game_share_bot.core.handlers.games.game.format_game_full") as mock_format, \
             patch("game_share_bot.core.handlers.games.game.enter_queue_kb") as mock_kb:

            mock_game_repo = AsyncMock()
            mock_disc_repo = AsyncMock()
            mock_user_repo = AsyncMock()
            mock_game_repo_class.return_value = mock_game_repo
            mock_disc_repo_class.return_value = mock_disc_repo
            mock_user_repo_class.return_value = mock_user_repo

            game = MagicMock(
                id=1,
                title="Test Game",
                description="Desc",
                cover_image_url=None,
                queues=[],
            )
            user = MagicMock(id=10, rentals=[], queues=[])
            mock_game_repo.get_by_id.return_value = game
            mock_user_repo.get_by_tg_id.return_value = user
            mock_disc_repo.get_available_discs_count_by_game.return_value = 1
            mock_get_pos.return_value = None
            mock_format.return_value = "FULL_INFO"
            mock_kb.return_value = "KB"

            mock_message.text = "/game_1"

            from game_share_bot.core.handlers.games.game import cmd_game
            await cmd_game(mock_message, test_session)

            mock_message.answer.assert_called_once()
            text = mock_message.answer.call_args.args[0]
            assert text == "FULL_INFO"
            assert mock_message.answer.call_args.kwargs["reply_markup"] == "KB"

    @pytest.mark.asyncio
    async def test_cmd_game_not_found(self, mock_message, test_session):
        with patch("game_share_bot.core.handlers.games.game.GameRepository") as mock_game_repo_class:
            mock_game_repo = AsyncMock()
            mock_game_repo_class.return_value = mock_game_repo

            mock_game_repo.get_by_id.return_value = None
            mock_message.text = "/game_999"

            from game_share_bot.core.handlers.games.game import cmd_game
            await cmd_game(mock_message, test_session)

            mock_game_repo.get_by_id.assert_awaited_once_with(999)
            mock_message.answer.assert_called_once()
            assert "Игра не найдена" in mock_message.answer.call_args.args[0]

