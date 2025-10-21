import pytest
from unittest.mock import patch, AsyncMock

class TestMainMenuHandlers:
    @pytest.mark.asyncio
    async def test_main_menu_from_message(self, mock_message, mock_state):
        with patch('game_share_bot.core.handlers.menu.main.main_menu_kb') as mock_kb:
            mock_kb.return_value = "mock_main_menu_kb"

            from game_share_bot.core.handlers.menu.main import main_menu
            await main_menu(mock_message, mock_state)

            mock_state.clear.assert_called_once()
            mock_message.answer.assert_called_with("Главное меню", reply_markup="mock_main_menu_kb")

    @pytest.mark.asyncio
    async def test_handle_help_from_message(self, mock_message):
        with patch('game_share_bot.core.handlers.menu.main.return_kb') as mock_return_kb:
            mock_return_kb.return_value = "mock_return_kb"

            from game_share_bot.core.handlers.menu.main import handle_help
            await handle_help(mock_message)

            mock_message.answer.assert_called_with("@cynpy_the_best", reply_markup="mock_return_kb")