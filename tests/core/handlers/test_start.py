import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from aiogram.types import ReplyKeyboardRemove

from game_share_bot.core.handlers.start import cmd_start, handle_phone_number
from game_share_bot.core.states import RegisterState


class TestStartHandlers:
    @pytest.mark.asyncio
    async def test_cmd_start_new_user(self, mock_message, mock_session, mock_state):
        with patch('game_share_bot.core.handlers.start.UserRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_by_tg_id.return_value = None

            with patch('game_share_bot.core.handlers.start.register_kb') as mock_register_kb:
                mock_register_kb.return_value = "mock_register_keyboard"

                await cmd_start(mock_message, mock_session, mock_state)

                mock_state.clear.assert_called_once()
                mock_message.answer.assert_called_once_with(
                    "Пожалуйста, поделитесь номером телефона для регистрации",
                    reply_markup="mock_register_keyboard"
                )
                mock_state.set_state.assert_called_once_with(RegisterState.waiting_for_phone)

    @pytest.mark.asyncio
    async def test_cmd_start_existing_user(self, mock_message, mock_session, mock_state):
        with patch('game_share_bot.core.handlers.start.UserRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_by_tg_id.return_value = MagicMock()

            with patch('game_share_bot.core.handlers.start.main_menu') as mock_main_menu:
                await cmd_start(mock_message, mock_session, mock_state)

                mock_state.clear.assert_called_once()
                mock_main_menu.assert_called_once_with(mock_message, mock_state)

    @pytest.mark.asyncio
    async def test_handle_phone_number_success(self, mock_message_with_contact, mock_session, mock_state):
        with patch('game_share_bot.core.handlers.start.UserRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.try_create.return_value = MagicMock()

            with patch('game_share_bot.core.handlers.start.main_menu_kb') as mock_main_menu_kb:
                mock_main_menu_kb.return_value = "mock_main_menu_kb"

                await handle_phone_number(mock_message_with_contact, mock_session, mock_state)

                mock_state.clear.assert_called_once()
                mock_message_with_contact.answer.assert_any_call(
                    "✅ Номер +1234567890 сохранён! Регистрация завершена.",
                    reply_markup=ReplyKeyboardRemove()
                )
                mock_message_with_contact.answer.assert_any_call(
                    "Главное меню",
                    reply_markup="mock_main_menu_kb"
                )

    @pytest.mark.asyncio
    async def test_handle_phone_number_error(self, mock_message_with_contact, mock_session, mock_state):
        with patch('game_share_bot.core.handlers.start.UserRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.try_create.return_value = None

            await handle_phone_number(mock_message_with_contact, mock_session, mock_state)

            mock_state.clear.assert_called_once()
            mock_message_with_contact.answer.assert_called_with(
                "Произошла непредвиденная ошибка! Обратись в поддержку",
                reply_markup=ReplyKeyboardRemove()
            )

    @pytest.mark.asyncio
    async def test_handle_phone_number_with_plus_prefix(self, mock_message_with_contact, mock_session, mock_state):
        mock_message_with_contact.contact.phone_number = "+1234567890"

        with patch('game_share_bot.core.handlers.start.UserRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.try_create.return_value = MagicMock()

            await handle_phone_number(mock_message_with_contact, mock_session, mock_state)

            # Исправляем: убираем role из проверки, так как в реальном коде он передается как None по умолчанию
            mock_repo.try_create.assert_called_once_with(
                tg_id=123,
                phone="+1234567890",
                name="test_user"
                # role=None передается по умолчанию, но не явно в вызове
            )