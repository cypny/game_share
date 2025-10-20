import pytest
from unittest.mock import patch, AsyncMock

from game_share_bot.core.handlers.menu.main import main_menu, handle_help


class TestMainMenuHandlers:
    @pytest.mark.asyncio
    async def test_main_menu_from_message(self, mock_message, mock_state):
        with patch('game_share_bot.core.handlers.menu.main.main_menu_kb') as mock_kb:
            mock_kb.return_value = "mock_main_menu_kb"

            await main_menu(mock_message, mock_state)

            mock_state.clear.assert_called_once()
            mock_message.answer.assert_called_with("Главное меню", reply_markup="mock_main_menu_kb")

    @pytest.mark.asyncio
    async def test_main_menu_from_callback(self, mock_callback_query, mock_state):
        with patch('game_share_bot.core.handlers.menu.main.main_menu_kb') as mock_kb:
            mock_kb.return_value = "mock_main_menu_kb"

            await main_menu(mock_callback_query, mock_state)

            mock_state.clear.assert_called_once()
            # Для callback используем edit_text вместо answer
            mock_callback_query.message.edit_text.assert_called_with("Главное меню", reply_markup="mock_main_menu_kb")

    @pytest.mark.asyncio
    async def test_handle_help_from_message(self, mock_message):
        with patch('game_share_bot.core.handlers.menu.main.return_kb') as mock_return_kb:
            mock_return_kb.return_value = "mock_return_kb"

            await handle_help(mock_message)

            mock_message.answer.assert_called_with("@cynpy_the_best", reply_markup="mock_return_kb")

    @pytest.mark.asyncio
    async def test_handle_help_from_callback(self, mock_callback_query):
        with patch('game_share_bot.core.handlers.menu.main.return_kb') as mock_return_kb:
            mock_return_kb.return_value = "mock_return_kb"

            await handle_help(mock_callback_query)

            mock_callback_query.message.edit_text.assert_called_with("@cynpy_the_best", reply_markup="mock_return_kb")