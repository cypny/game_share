import pytest
from unittest.mock import AsyncMock, patch
from aiogram.types import CallbackQuery, User
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import MenuCallback
from game_share_bot.domain.enums import MenuSection
from game_share_bot.infrastructure.models import User as UserModel


class TestPersonalCabinetHandlers:
    """Тесты для хендлеров личного кабинета"""

    @pytest.mark.asyncio
    async def test_personal_cabinet_success(self, test_session, mock_callback_query):
        """Тест успешного открытия личного кабинета"""
        from game_share_bot.core.handlers.menu.personal_cabinet import personal_cabinet

        # Создаем тестового пользователя в БД
        user_repo = AsyncMock()
        test_user = UserModel(
            id=1,
            tg_id=123,
            phone="+79991234567",
            name="Test User",
            role="user"
        )
        user_repo.get_by_tg_id = AsyncMock(return_value=test_user)

        # Мокаем репозиторий
        with patch('game_share_bot.core.handlers.menu.personal_cabinet.UserRepository', return_value=user_repo):
            await personal_cabinet(mock_callback_query, test_session, AsyncMock())

        # Проверяем, что сообщение было отредактировано с правильным текстом
        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args
        assert "👤 Личный кабинет" in call_args[0][0]
        assert "+79991234567" in call_args[0][0]

        # Проверяем, что был вызван ответ
        mock_callback_query.answer.assert_not_called()  # Не должно быть answer при успехе

    @pytest.mark.asyncio
    async def test_personal_cabinet_user_not_found(self, test_session, mock_callback_query):
        """Тест открытия личного кабинета когда пользователь не найден"""
        from game_share_bot.core.handlers.menu.personal_cabinet import personal_cabinet

        user_repo = AsyncMock()
        user_repo.get_by_tg_id = AsyncMock(return_value=None)

        with patch('game_share_bot.core.handlers.menu.personal_cabinet.UserRepository', return_value=user_repo):
            await personal_cabinet(mock_callback_query, test_session, AsyncMock())

        # Проверяем, что был вызван answer с ошибкой
        mock_callback_query.answer.assert_called_once_with("❌ Пользователь не найден")
        mock_callback_query.message.edit_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_personal_cabinet_exception(self, test_session, mock_callback_query):
        """Тест обработки исключения при открытии личного кабинета"""
        from game_share_bot.core.handlers.menu.personal_cabinet import personal_cabinet

        user_repo = AsyncMock()
        user_repo.get_by_tg_id = AsyncMock(side_effect=Exception("DB error"))

        with patch('game_share_bot.core.handlers.menu.personal_cabinet.UserRepository', return_value=user_repo):
            await personal_cabinet(mock_callback_query, test_session, AsyncMock())

        # Проверяем, что был вызван answer с ошибкой
        mock_callback_query.answer.assert_called_once_with("❌ Ошибка при загрузке личного кабинета")

    @pytest.mark.asyncio
    async def test_manage_subscription(self, mock_callback_query):
        """Тест кнопки управления подпиской"""
        from game_share_bot.core.handlers.menu.personal_cabinet import manage_subscription

        await manage_subscription(mock_callback_query)

        mock_callback_query.answer.assert_called_once_with("📦 Функционал 'Управление подпиской' в разработке")

    @pytest.mark.asyncio
    async def test_my_queue(self, mock_callback_query):
        """Тест кнопки просмотра очереди"""
        from game_share_bot.core.handlers.menu.personal_cabinet import my_queue

        await my_queue(mock_callback_query)

        mock_callback_query.answer.assert_called_once_with("📋 Функционал 'Моя очередь' в разработке")

    @pytest.mark.asyncio
    async def test_personal_cabinet_state_cleared(self, test_session, mock_callback_query, mock_state):
        """Тест очистки состояния при открытии личного кабинета"""
        from game_share_bot.core.handlers.menu.personal_cabinet import personal_cabinet

        user_repo = AsyncMock()
        test_user = UserModel(
            id=1,
            tg_id=123,
            phone="+79991234567",
            name="Test User",
            role="user"
        )
        user_repo.get_by_tg_id = AsyncMock(return_value=test_user)

        with patch('game_share_bot.core.handlers.menu.personal_cabinet.UserRepository', return_value=user_repo):
            await personal_cabinet(mock_callback_query, test_session, mock_state)

        # Проверяем, что состояние было очищено
        mock_state.clear.assert_called_once()