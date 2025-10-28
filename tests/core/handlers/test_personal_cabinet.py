import pytest
from unittest.mock import AsyncMock, patch
from game_share_bot.infrastructure.models import User as UserModel


class TestPersonalCabinetHandlers:
    @pytest.mark.asyncio
    async def test_personal_cabinet_success(self, test_session, mock_callback_query):
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
            await personal_cabinet(mock_callback_query, test_session, AsyncMock())

            mock_callback_query.message.edit_text.assert_called_once()
            call_args = mock_callback_query.message.edit_text.call_args
            assert "👤 Личный кабинет" in call_args[0][0]
            assert "+79991234567" in call_args[0][0]

            mock_callback_query.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_personal_cabinet_user_not_found(self, test_session, mock_callback_query):
        from game_share_bot.core.handlers.menu.personal_cabinet import personal_cabinet

        user_repo = AsyncMock()
        user_repo.get_by_tg_id = AsyncMock(return_value=None)

        with patch('game_share_bot.core.handlers.menu.personal_cabinet.UserRepository', return_value=user_repo):
            await personal_cabinet(mock_callback_query, test_session, AsyncMock())

            mock_callback_query.answer.assert_called_once_with("❌ Пользователь не найден")
            mock_callback_query.message.edit_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_personal_cabinet_exception(self, test_session, mock_callback_query):
        from game_share_bot.core.handlers.menu.personal_cabinet import personal_cabinet

        user_repo = AsyncMock()
        user_repo.get_by_tg_id = AsyncMock(side_effect=Exception("DB error"))

        with patch('game_share_bot.core.handlers.menu.personal_cabinet.UserRepository', return_value=user_repo):
            await personal_cabinet(mock_callback_query, test_session, AsyncMock())

            mock_callback_query.answer.assert_called_once_with("❌ Ошибка при загрузке личного кабинета")

    @pytest.mark.asyncio
    async def test_manage_subscription(self, mock_callback_query):
        from game_share_bot.core.handlers.menu.personal_cabinet import manage_subscription

        await manage_subscription(mock_callback_query)

        mock_callback_query.answer.assert_called_once_with("📦 Функционал 'Управление подпиской' в разработке")

    @pytest.mark.asyncio
    async def test_my_queue(self, mock_callback_query):
        from game_share_bot.core.handlers.menu.personal_cabinet import my_queue

        await my_queue(mock_callback_query)

        mock_callback_query.answer.assert_called_once_with("📋 Функционал 'Моя очередь' в разработке")

    @pytest.mark.asyncio
    async def test_personal_cabinet_state_cleared(self, test_session, mock_callback_query, mock_state):
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

            mock_state.clear.assert_called_once()