import pytest
from unittest.mock import patch, AsyncMock
from aiogram.types import ReplyKeyboardRemove

from game_share_bot.core.states.user import RegisterState


class TestStartHandlers:
    @pytest.mark.asyncio
    async def test_cmd_start_new_user(self, mock_message, mock_session, mock_state):
        with patch('game_share_bot.core.handlers.start.UserRepository') as mock_repo_class, \
                patch('game_share_bot.core.handlers.start.register_kb') as mock_register_kb:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_by_tg_id.return_value = None
            mock_register_kb.return_value = "mock_register_keyboard"

            from game_share_bot.core.handlers.start import cmd_start
            await cmd_start(mock_message, mock_session, mock_state)

            mock_state.clear.assert_called_once()
            mock_message.answer.assert_called_once_with(
                "Пожалуйста, поделитесь номером телефона для регистрации",
                reply_markup="mock_register_keyboard"
            )
            mock_state.set_state.assert_called_once_with(RegisterState.waiting_for_phone)

    @pytest.mark.asyncio
    async def test_cmd_start_existing_user(self, mock_message, mock_session, mock_state):
        with patch('game_share_bot.core.handlers.start.UserRepository') as mock_repo_class, \
                patch('game_share_bot.core.handlers.start.main_menu') as mock_main_menu:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_by_tg_id.return_value = AsyncMock()

            from game_share_bot.core.handlers.start import cmd_start
            await cmd_start(mock_message, mock_session, mock_state)

            mock_state.clear.assert_called_once()
            mock_main_menu.assert_called_once_with(mock_message, mock_state)

    @pytest.mark.asyncio
    async def test_handle_phone_number_success_integration(self, mock_message_with_contact, test_session, mock_state):
        """Интеграционный тест - проверяем сохранение пользователя в БД"""
        with patch('game_share_bot.core.handlers.start.main_menu_kb') as mock_main_menu_kb:
            mock_main_menu_kb.return_value = "mock_main_menu_kb"

            mock_message_with_contact.from_user.id = 123
            mock_message_with_contact.from_user.full_name = "testuser"
            mock_message_with_contact.contact.phone_number = "+1234567890"

            from game_share_bot.core.handlers.start import handle_phone_number
            await handle_phone_number(mock_message_with_contact, test_session, mock_state)

            from game_share_bot.infrastructure.repositories.user import UserRepository
            user_repo = UserRepository(test_session)
            saved_user = await user_repo.get_by_tg_id(123)

            assert saved_user is not None
            assert saved_user.tg_id == 123
            assert saved_user.phone == "+1234567890"
            assert saved_user.name == "testuser"

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

            from game_share_bot.core.handlers.start import handle_phone_number
            await handle_phone_number(mock_message_with_contact, mock_session, mock_state)

            mock_state.clear.assert_called_once()
            mock_message_with_contact.answer.assert_called_with(
                "Произошла непредвиденная ошибка! Обратись в поддержку",
                reply_markup=ReplyKeyboardRemove()
            )