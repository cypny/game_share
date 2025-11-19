import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from game_share_bot.infrastructure.repositories.subscription.subscription import SubscriptionRepository


class TestSubscriptionRepository:
    @pytest.mark.asyncio
    async def test_get_by_user_success(self, test_session, mock_user, mock_subscription):
        repo = SubscriptionRepository(test_session)

        with patch('game_share_bot.infrastructure.repositories.subscription.subscription.BaseRepository.get_by_field',
                   new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_subscription

            result = await repo.get_all_by_user(mock_user)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "user_id"
            assert call_args[0][1] == mock_user.id
            assert len(call_args[1]['options']) == 1
            assert result == mock_subscription
            assert result.user.id == mock_user.id
            assert result.plan.name == "premium"

    @pytest.mark.asyncio
    async def test_get_by_user_not_found(self, test_session, mock_user):
        repo = SubscriptionRepository(test_session)

        with patch('game_share_bot.infrastructure.repositories.subscription.subscription.BaseRepository.get_by_field',
                   new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            result = await repo.get_all_by_user(mock_user)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "user_id"
            assert call_args[0][1] == mock_user.id
            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_with_relations(self, test_session, mock_user, mock_subscription):
        repo = SubscriptionRepository(test_session)

        with patch('game_share_bot.infrastructure.repositories.subscription.subscription.BaseRepository.get_by_field',
                   new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_subscription

            result = await repo.get_all_by_user(mock_user)

            assert result is not None
            assert result.user is not None
            assert result.plan is not None
            assert result.plan.max_simultaneous_rental == 5
            assert result.plan.monthly_price == 999.99

    @pytest.mark.asyncio
    async def test_create_subscription(self, test_session, mock_user, mock_subscription_plan):
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
            from game_share_bot.infrastructure.models import Subscription
            subscription = Subscription(**subscription_data)
            mock_create.return_value = subscription

            result = await repo.create(**subscription_data)

            mock_create.assert_called_once_with(**subscription_data)
            assert result.user_id == mock_user.id
            assert result.plan_id == mock_subscription_plan.id

    @pytest.mark.asyncio
    async def test_update_subscription(self, test_session, mock_subscription):
        repo = SubscriptionRepository(test_session)

        with patch('game_share_bot.infrastructure.repositories.subscription.subscription.BaseRepository.update',
                   new_callable=AsyncMock) as mock_update:
            updated_subscription = mock_subscription
            mock_update.return_value = updated_subscription

            result = await repo.update(mock_subscription.id, is_auto_renewal=False)

            mock_update.assert_called_once_with(mock_subscription.id, is_auto_renewal=False)
            assert result is not None