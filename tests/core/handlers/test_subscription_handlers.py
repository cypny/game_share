import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from game_share_bot.core.callbacks.subscription import SubscriptionCallback
from game_share_bot.domain.enums.subscription.action import SubscriptionAction
from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.core.states.subscription.subscribe import SubscriptionState


class TestSubscriptionHandlers:
    @pytest.mark.asyncio
    async def test_subscription_info_and_buying_with_subscription(
        self,
        mock_callback_query,
        mock_state,
        mock_user,
        mock_subscription,
    ):
        from game_share_bot.core.handlers.user import subscription as handlers

        session = AsyncMock()

        with patch.object(handlers, "UserRepository") as user_repo_cls, \
             patch.object(handlers, "SubscriptionRepository") as sub_repo_cls, \
             patch.object(handlers, "format_subscription_info") as format_info, \
             patch.object(handlers, "subscription_actions_kb") as actions_kb:

            user_repo = AsyncMock()
            sub_repo = AsyncMock()
            user_repo_cls.return_value = user_repo
            sub_repo_cls.return_value = sub_repo

            user_repo.get_by_tg_id.return_value = mock_user

            # Создаем активную подписку
            mock_subscription.status = SubscriptionStatus.ACTIVE
            sub_repo.get_all_by_user.return_value = [mock_subscription]

            plan = MagicMock(id=1, name="TestPlan")
            session.scalars.return_value = AsyncMock(__iter__=lambda self: iter([plan]))

            format_info.return_value = "SUB_INFO"
            actions_kb.return_value = "KB"

            await handlers.subscription_info_and_buying(
                mock_callback_query,
                session,
                mock_state,
            )

            user_repo.get_by_tg_id.assert_awaited_once_with(
                mock_callback_query.from_user.id
            )
            sub_repo.get_all_by_user.assert_awaited_once_with(mock_user)

            mock_callback_query.message.edit_text.assert_called_once_with(
                text="SUB_INFO",
                reply_markup="KB",
                parse_mode="HTML",
            )

    @pytest.mark.asyncio
    async def test_subscription_info_and_buying_no_subscription(
        self,
        mock_callback_query,
        mock_state,
        mock_user,
    ):
        from game_share_bot.core.handlers.user import subscription as handlers

        session = AsyncMock()

        with patch.object(handlers, "UserRepository") as user_repo_cls, \
             patch.object(handlers, "SubscriptionRepository") as sub_repo_cls, \
             patch.object(handlers, "format_subscription_info") as format_info, \
             patch.object(handlers, "subscription_actions_kb") as actions_kb:

            user_repo = AsyncMock()
            sub_repo = AsyncMock()
            user_repo_cls.return_value = user_repo
            sub_repo_cls.return_value = sub_repo

            user_repo.get_by_tg_id.return_value = mock_user
            sub_repo.get_all_by_user.return_value = []  # Нет подписок

            plan = MagicMock(id=1, name="TestPlan")
            session.scalars.return_value = AsyncMock(__iter__=lambda self: iter([plan]))

            format_info.return_value = "NO_SUB"
            actions_kb.return_value = "KB"

            await handlers.subscription_info_and_buying(
                mock_callback_query,
                session,
                mock_state,
            )

            mock_callback_query.message.edit_text.assert_called_once()
            _, kwargs = mock_callback_query.message.edit_text.call_args
            assert "NO_SUB" in kwargs["text"]
            assert kwargs["reply_markup"] == "KB"
            assert kwargs["parse_mode"] == "HTML"

    @pytest.mark.asyncio
    async def test_select_subscription_duration(self, mock_callback_query, mock_state):
        from game_share_bot.core.handlers.user import subscription as handlers

        session = AsyncMock()
        plan = MagicMock(id=10, name="Premium")
        session.scalar.return_value = plan

        with patch.object(handlers, "select_duration_kb") as duration_kb:
            duration_kb.return_value = "KB"

            callback_data = SubscriptionCallback(
                action=SubscriptionAction.SELECT_DURATION,
                subscription_type=plan.id,
            )

            await handlers.select_subscription_duration(
                mock_callback_query,
                callback_data,
                session,
                mock_state,
            )

            mock_state.update_data.assert_awaited_once_with(
                plan_id=plan.id,
                plan_name=plan.name,
            )
            mock_callback_query.message.edit_text.assert_called_once()
            _, kwargs = mock_callback_query.message.edit_text.call_args
            assert "Подписка:" in kwargs["text"]
            assert kwargs["reply_markup"] == "KB"
            assert kwargs["parse_mode"] == "HTML"
            mock_state.set_state.assert_awaited_once_with(
                SubscriptionState.choosing_duration
            )

    @pytest.mark.asyncio
    async def test_confirm_subscription_buy(self, mock_callback_query, mock_state):
        from game_share_bot.core.handlers.user import subscription as handlers

        with patch.object(handlers, "confirm_subscription_buy_kb") as kb_factory:
            kb_factory.return_value = "KB"

            mock_state.get_data.return_value = {
                "plan_name": "Premium",
                "duration": 3,
            }

            callback_data = SubscriptionCallback(
                action=SubscriptionAction.CONFIRM_BUY,
                month_duration=3,
            )

            await handlers.confirm_subscription_buy(
                mock_callback_query,
                callback_data,
                mock_state,
            )

            mock_callback_query.message.edit_text.assert_called_once()
            _, kwargs = mock_callback_query.message.edit_text.call_args
            assert "Подтвердите данные:" in kwargs["text"]
            assert "Premium" in kwargs["text"]
            assert "3" in kwargs["text"]
            assert kwargs["reply_markup"] == "KB"
            assert kwargs["parse_mode"] == "HTML"
            mock_state.set_state.assert_awaited_once_with(
                SubscriptionState.confirming
            )

    @pytest.mark.asyncio
    async def test_purchase_subscription_success(
        self,
        mock_callback_query,
        mock_state,
        mock_user,
    ):
        from game_share_bot.core.handlers.user import subscription as handlers

        session = AsyncMock()

        with patch.object(handlers, "UserRepository") as user_repo_cls, \
             patch.object(handlers, "SubscriptionRepository") as sub_repo_cls, \
             patch.object(handlers, "create_payment") as mock_create_payment, \
             patch.object(handlers, "select") as mock_select:

            user_repo = AsyncMock()
            sub_repo = AsyncMock()
            user_repo_cls.return_value = user_repo
            sub_repo_cls.return_value = sub_repo

            user_repo.get_by_tg_id.return_value = mock_user
            sub_repo.get_all_by_user.return_value = []  # Нет активных подписок

            mock_state.get_data.return_value = {
                "plan_id": 1,
                "plan_name": "Premium",
                "duration": 3,
            }

            # Мокаем session.scalar для получения плана
            mock_plan = MagicMock()
            mock_plan.id = 1
            mock_plan.name = "Premium"
            session.scalar = AsyncMock(return_value=mock_plan)

            # Мокаем create_payment
            mock_create_payment.return_value = ("payment_123", "https://payment.url")

            sub_repo.create.return_value = MagicMock(id=100)

            await handlers.purchase_subscription(
                mock_callback_query,
                session,
                mock_state,
            )

            sub_repo.create.assert_awaited()
            mock_callback_query.message.edit_text.assert_called_once()
            mock_state.clear.assert_awaited_once()