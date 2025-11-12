import pytest
from unittest.mock import patch, AsyncMock


class TestCatalogHandlers:
    @pytest.mark.asyncio
    async def test_catalog_success(self, mock_callback_query, test_session):
        from game_share_bot.core.callbacks import CatalogCallback

        with patch('game_share_bot.core.handlers.games.catalog.GameRepository') as mock_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.format_games_list') as mock_format, \
                patch('game_share_bot.core.handlers.games.catalog.catalog_keyboard') as mock_kb:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_all_with_available_discs.return_value = ["game1", "game2"]
            mock_repo.count_all_with_available_discs.return_value = 2

            mock_format.return_value = "formatted_games"
            mock_kb.return_value = "mock_keyboard"

            # query обязателен и строка
            callback_data = CatalogCallback(query="", page=0)

            from game_share_bot.core.handlers.games.catalog import catalog
            await catalog(mock_callback_query, callback_data, test_session)

            mock_repo.get_all_with_available_discs.assert_awaited_once_with(
                skip=0,
                take=7,
            )
            mock_repo.count_all_with_available_discs.assert_awaited_once()

            mock_format.assert_called_once_with(["game1", "game2"])
            mock_kb.assert_called_once()

            mock_callback_query.answer.assert_called_once()
            mock_callback_query.message.edit_text.assert_called_once()

            call_args = mock_callback_query.message.edit_text.call_args
            text = call_args.args[0]

            assert "Каталог игр:" in text
            assert "formatted_games" in text
            assert call_args.kwargs.get("reply_markup") == "mock_keyboard"
            assert call_args.kwargs.get("parse_mode") == "HTML"

    @pytest.mark.asyncio
    async def test_catalog_empty(self, mock_callback_query, test_session):
        from game_share_bot.core.callbacks import CatalogCallback

        with patch('game_share_bot.core.handlers.games.catalog.GameRepository') as mock_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.format_games_list') as mock_format, \
                patch('game_share_bot.core.handlers.games.catalog.catalog_keyboard') as mock_kb:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_all_with_available_discs.return_value = []
            mock_repo.count_all_with_available_discs.return_value = 0

            mock_format.return_value = ""
            mock_kb.return_value = "mock_keyboard"

            callback_data = CatalogCallback(query="", page=0)

            from game_share_bot.core.handlers.games.catalog import catalog
            await catalog(mock_callback_query, callback_data, test_session)

            mock_repo.get_all_with_available_discs.assert_awaited_once_with(
                skip=0,
                take=7,
            )
            mock_repo.count_all_with_available_discs.assert_awaited_once()
            mock_format.assert_called_once_with([])

            mock_callback_query.message.edit_text.assert_called_once()
            call_args = mock_callback_query.message.edit_text.call_args
            text = call_args.args[0]

            assert "Каталог игр:" in text
            assert call_args.kwargs.get("reply_markup") == "mock_keyboard"

    @pytest.mark.asyncio
    async def test_catalog_error(self, mock_callback_query, test_session):
        from game_share_bot.core.callbacks import CatalogCallback

        with patch('game_share_bot.core.handlers.games.catalog.GameRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

            mock_repo.get_all_with_available_discs.side_effect = Exception("DB error")

            callback_data = CatalogCallback(query="", page=0)

            from game_share_bot.core.handlers.games.catalog import catalog
            await catalog(mock_callback_query, callback_data, test_session)

            mock_callback_query.answer.assert_called_with("❌ Ошибка при загрузке каталога")
            mock_callback_query.message.edit_text.assert_not_called()
