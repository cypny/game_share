import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from aiogram.types import CallbackQuery, Message

from game_share_bot.core.callbacks import CatalogCallback
from game_share_bot.core.handlers.games import catalog as handlers


class TestCatalogHandlers:
    @pytest.mark.asyncio
    async def test_catalog_success(self, test_session):
        mock_message = AsyncMock(spec=Message)
        mock_message.edit_text = AsyncMock()

        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.message = mock_message
        mock_callback.answer = AsyncMock()

        callback_data = CatalogCallback(query="", page=0)

        with patch.object(handlers, "GameRepository") as repo_cls, \
             patch.object(handlers, "format_games_list") as format_games_list, \
             patch.object(handlers, "catalog_keyboard") as catalog_keyboard:

            repo = AsyncMock()
            repo_cls.return_value = repo

            game = MagicMock()
            game.title = "Test Game"
            repo.get_all.return_value = [game]
            repo.count_all.return_value = 1

            format_games_list.return_value = "formatted_games"
            catalog_keyboard.return_value = "keyboard"

            await handlers.catalog(mock_callback, callback_data, test_session)

            repo_cls.assert_called_once_with(test_session)
            repo.get_all.assert_awaited_once_with(skip=0, take=10)
            repo.count_all.assert_awaited_once()

            format_games_list.assert_called_once()
            catalog_keyboard.assert_called_once()

            mock_callback.answer.assert_awaited_once()

            mock_message.edit_text.assert_called_once()
            args, kwargs = mock_message.edit_text.call_args
            assert "Каталог игр (" in args[0]
            assert "formatted_games" in args[0]
            assert kwargs["parse_mode"] == "HTML"
            assert kwargs["reply_markup"] == "keyboard"

    @pytest.mark.asyncio
    async def test_catalog_empty(self, test_session):
        mock_message = AsyncMock(spec=Message)
        mock_message.edit_text = AsyncMock()

        mock_callback = AsyncMock(spec=CallbackQuery)
        mock_callback.message = mock_message
        mock_callback.answer = AsyncMock()

        callback_data = CatalogCallback(query="", page=0)

        with patch.object(handlers, "GameRepository") as repo_cls, \
             patch.object(handlers, "format_games_list") as format_games_list, \
             patch.object(handlers, "catalog_keyboard") as catalog_keyboard:

            repo = AsyncMock()
            repo_cls.return_value = repo

            repo.get_all.return_value = []
            repo.count_all.return_value = 0

            format_games_list.return_value = "Нет игр"
            catalog_keyboard.return_value = "keyboard"

            await handlers.catalog(mock_callback, callback_data, test_session)

            repo_cls.assert_called_once_with(test_session)
            repo.get_all.assert_awaited_once_with(skip=0, take=10)
            repo.count_all.assert_awaited_once()

            mock_callback.answer.assert_awaited_once()

            mock_message.edit_text.assert_called_once()
            args, kwargs = mock_message.edit_text.call_args
            assert "Каталог игр (" in args[0]
            assert "Нет игр" in args[0]
            assert kwargs["parse_mode"] == "HTML"
            assert kwargs["reply_markup"] == "keyboard"
