import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from aiogram.types import CallbackQuery

from game_share_bot.core.callbacks import GameCallback


class TestGamePageHandlers:
    """Тесты для страницы игры через callback"""

    @pytest.mark.asyncio
    async def test_open_game_page_success(self, mock_callback_query, test_session):
        """Тест успешного открытия страницы игры"""
        with patch('game_share_bot.core.handlers.games.game.GameRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            # Создаем тестовую игру
            test_game = MagicMock(
                id=1,
                title="Test Game",
                description="Test Description",
                cover_image_url="https://example.com/cover.jpg"
            )
            mock_repo.get_by_id.return_value = test_game

            # Создаем callback данные
            callback_data = GameCallback(action="open", game_id=1)

            from game_share_bot.core.handlers.games.game import open_game_page
            await open_game_page(mock_callback_query, callback_data, test_session)

            # Проверяем вызовы
            mock_repo.get_by_id.assert_called_with(1)
            mock_callback_query.message.answer_photo.assert_called_once()

            call_args = mock_callback_query.message.answer_photo.call_args
            assert call_args[1]['photo'] == "https://example.com/cover.jpg"
            assert "Test Game" in call_args[1]['caption']

    @pytest.mark.asyncio
    async def test_open_game_page_not_found(self, mock_callback_query, test_session):
        """Тест когда игра не найдена"""
        with patch('game_share_bot.core.handlers.games.game.GameRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_by_id.return_value = None

            callback_data = GameCallback(action="open", game_id=999)

            from game_share_bot.core.handlers.games.game import open_game_page
            await open_game_page(mock_callback_query, callback_data, test_session)

            mock_callback_query.answer.assert_called_with("Игра не найдена")

    @pytest.mark.asyncio
    async def test_open_game_page_error(self, mock_callback_query, test_session):
        """Тест обработки ошибки"""
        with patch('game_share_bot.core.handlers.games.game.GameRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_by_id.side_effect = Exception("DB error")

            callback_data = GameCallback(action="open", game_id=1)

            from game_share_bot.core.handlers.games.game import open_game_page
            await open_game_page(mock_callback_query, callback_data, test_session)

            mock_callback_query.answer.assert_called_with("❌ Ошибка при загрузке информации об игре")