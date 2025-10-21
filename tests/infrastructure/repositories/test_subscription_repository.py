import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from game_share_bot.infrastructure.repositories.subscription.subscription import SubscriptionRepository


class TestSubscriptionRepository:
    """Тесты для SubscriptionRepository"""

    @pytest.mark.asyncio
    async def test_get_by_user_success(self, test_session, mock_user, mock_subscription):
        """Тест успешного получения подписки пользователя"""
        repo = SubscriptionRepository(test_session)

        # Правильный способ мока - патчим метод в классе, а не в экземпляре
        with patch('game_share_bot.infrastructure.repositories.subscription.subscription.BaseRepository.get_by_field',
                   new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_subscription

            result = await repo.get_by_user(mock_user)

            # Проверяем, что метод был вызван
            mock_get.assert_called_once()

            # Проверяем аргументы вызова
            call_args = mock_get.call_args
            assert call_args[0][0] == "user_id"  # field_name
            assert call_args[0][1] == mock_user.id  # value

            # Проверяем, что options переданы (joinedload)
            assert len(call_args[1]['options']) == 1

            # Проверяем результат
            assert result == mock_subscription
            assert result.user.id == mock_user.id
            assert result.plan.name == "premium"

    @pytest.mark.asyncio
    async def test_get_by_user_not_found(self, test_session, mock_user):
        """Тест получения подписки, когда у пользователя нет подписки"""
        repo = SubscriptionRepository(test_session)

        with patch('game_share_bot.infrastructure.repositories.subscription.subscription.BaseRepository.get_by_field',
                   new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            result = await repo.get_by_user(mock_user)

            mock_get.assert_called_once()

            call_args = mock_get.call_args
            assert call_args[0][0] == "user_id"
            assert call_args[0][1] == mock_user.id

            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_with_relations(self, test_session, mock_user, mock_subscription):
        """Тест получения подписки с загруженными отношениями"""
        repo = SubscriptionRepository(test_session)

        with patch('game_share_bot.infrastructure.repositories.subscription.subscription.BaseRepository.get_by_field',
                   new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_subscription

            result = await repo.get_by_user(mock_user)

            # Проверяем, что отношения загружены
            assert result is not None
            assert result.user is not None
            assert result.plan is not None
            assert result.plan.max_simultaneous_rental == 5
            assert result.plan.monthly_price == 999.99

    @pytest.mark.asyncio
    async def test_create_subscription(self, test_session, mock_user, mock_subscription_plan):
        """Тест создания новой подписки"""
        repo = SubscriptionRepository(test_session)

        subscription_data = {
            "user_id": mock_user.id,
            "plan_id": mock_subscription_plan.id,
            "start_date": datetime(2024, 1, 1),
            "end_date": datetime(2024, 12, 31),
            "is_auto_renewal": True
        }

        with patch('game_share_bot.infrastructure.repositories.subscription.subscription.BaseRepository.create',
                   new_callable=AsyncMock) as mock_create:
            # Создаем реальный объект подписки для возврата
            from game_share_bot.infrastructure.models import Subscription
            subscription = Subscription(**subscription_data)
            mock_create.return_value = subscription

            result = await repo.create(**subscription_data)

            mock_create.assert_called_once_with(**subscription_data)
            assert result.user_id == mock_user.id
            assert result.plan_id == mock_subscription_plan.id

    @pytest.mark.asyncio
    async def test_update_subscription(self, test_session, mock_subscription):
        """Тест обновления подписки"""
        repo = SubscriptionRepository(test_session)

        with patch('game_share_bot.infrastructure.repositories.subscription.subscription.BaseRepository.update',
                   new_callable=AsyncMock) as mock_update:
            # Создаем копию для имитации обновления
            updated_subscription = mock_subscription
            mock_update.return_value = updated_subscription

            result = await repo.update(mock_subscription.id, is_auto_renewal=False)

            mock_update.assert_called_once_with(mock_subscription.id, is_auto_renewal=False)
            # В реальном коде здесь будет обновленный объект
            assert result is not None