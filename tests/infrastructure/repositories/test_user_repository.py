import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.infrastructure.repositories.user import UserRepository
from game_share_bot.infrastructure.models.user import User as UserModel


class TestUserRepository:
    """Unit-тесты с моками"""

    @pytest.mark.asyncio
    async def test_try_create_checks_phone_first(self, mock_session):
        """Проверяем, что сначала проверяется телефон, потом tg_id"""
        user_repo = UserRepository(mock_session)

        user_repo.get_by_phone = AsyncMock(return_value=None)
        user_repo.get_by_tg_id = AsyncMock(return_value=None)

        await user_repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="test_user"
        )

        # Проверяем порядок вызовов
        user_repo.get_by_phone.assert_called_once()
        user_repo.get_by_tg_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_try_create_stops_on_duplicate_phone(self, mock_session):
        """Проверяем, что при дубликате телефона tg_id не проверяется"""
        user_repo = UserRepository(mock_session)

        user_repo.get_by_phone = AsyncMock(return_value=MagicMock(spec=UserModel))
        user_repo.get_by_tg_id = AsyncMock(return_value=None)

        result = await user_repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="test_user"
        )

        assert result is None
        user_repo.get_by_phone.assert_called_once_with("+1234567890")
        user_repo.get_by_tg_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_try_create_stops_on_duplicate_tg_id(self, mock_session):
        """Проверяем, что при дубликате tg_id создание не происходит"""
        user_repo = UserRepository(mock_session)

        user_repo.get_by_phone = AsyncMock(return_value=None)
        user_repo.get_by_tg_id = AsyncMock(return_value=MagicMock(spec=UserModel))

        result = await user_repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="test_user"
        )

        assert result is None
        user_repo.get_by_phone.assert_called_once_with("+1234567890")
        user_repo.get_by_tg_id.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_get_by_tg_id(self, mock_session):
        user_repo = UserRepository(mock_session)
        user_repo.get_by_field = AsyncMock(return_value=MagicMock(spec=UserModel))

        result = await user_repo.get_by_tg_id(123)

        assert result is not None
        user_repo.get_by_field.assert_called_once_with("tg_id", 123)

    @pytest.mark.asyncio
    async def test_get_by_phone(self, mock_session):
        user_repo = UserRepository(mock_session)
        user_repo.get_by_field = AsyncMock(return_value=MagicMock(spec=UserModel))

        result = await user_repo.get_by_phone("+1234567890")

        assert result is not None
        user_repo.get_by_field.assert_called_once_with("phone", "+1234567890")

    @pytest.mark.asyncio
    async def test_make_admin_success(self, mock_session):
        user_repo = UserRepository(mock_session)
        mock_user = MagicMock(spec=UserModel)
        mock_user.role = "user"
        user_repo.get_by_tg_id = AsyncMock(return_value=mock_user)
        mock_session.commit = AsyncMock()

        result = await user_repo.make_admin(123)

        assert result is True
        assert mock_user.role == "admin"
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_admin_user_not_found(self, mock_session):
        user_repo = UserRepository(mock_session)
        user_repo.get_by_tg_id = AsyncMock(return_value=None)

        result = await user_repo.make_admin(123)

        assert result is False