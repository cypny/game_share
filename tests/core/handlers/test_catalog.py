import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from aiogram.types import CallbackQuery, Message

from game_share_bot.core.callbacks import CatalogCallback, MenuCallback
from game_share_bot.domain.enums import MenuSection


class TestCatalogHandlers:
    """Тесты для хендлеров каталога игр"""

    @pytest.mark.asyncio
    async def test_catalog_success(self, mock_callback_query, test_session):
        """Тест успешного отображения каталога"""
        with patch('game_share_bot.core.handlers.games.catalog.GameRepository') as mock_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.return_kb') as mock_return_kb:
            # Настраиваем моки
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            # Создаем тестовые игры
            test_games = [
                MagicMock(id=1, title="Game 1", description="Description 1"),
                MagicMock(id=2, title="Game 2", description="Description 2"),
            ]
            mock_repo.get_all.return_value = test_games
            mock_return_kb.return_value = "mock_return_keyboard"

            from game_share_bot.core.handlers.games.catalog import catalog
            await catalog(mock_callback_query, test_session)

            # Проверяем вызовы
            mock_repo.get_all.assert_called_once()
            mock_callback_query.answer.assert_called_once()
            mock_callback_query.message.edit_text.assert_called_once()

            # Проверяем содержимое сообщения
            call_args = mock_callback_query.message.edit_text.call_args
            assert "Каталог игр (2)" in call_args[0][0]
            assert "Game 1" in call_args[0][0]
            assert "Game 2" in call_args[0][0]
            assert "/game_1" in call_args[0][0]
            assert "/game_2" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_catalog_empty(self, mock_callback_query, test_session):
        """Тест каталога без игр"""
        with patch('game_share_bot.core.handlers.games.catalog.GameRepository') as mock_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.return_kb') as mock_return_kb:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_all.return_value = []
            mock_return_kb.return_value = "mock_return_keyboard"

            from game_share_bot.core.handlers.games.catalog import catalog
            await catalog(mock_callback_query, test_session)

            call_args = mock_callback_query.message.edit_text.call_args
            assert "Каталог игр (0)" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_catalog_error(self, mock_callback_query, test_session):
        """Тест обработки ошибки при загрузке каталога"""
        with patch('game_share_bot.core.handlers.games.catalog.GameRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_all.side_effect = Exception("DB error")

            from game_share_bot.core.handlers.games.catalog import catalog
            await catalog(mock_callback_query, test_session)

            mock_callback_query.answer.assert_called_with("❌ Ошибка при загрузке каталога")