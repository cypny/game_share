import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from game_share_bot.core.callbacks import GameCallback
from game_share_bot.domain.enums.actions.game_actions import GameAction


class TestTakeGameHandlers:
    @pytest.mark.asyncio
    async def test_take_game_success(self, mock_callback_query, test_session):
        from game_share_bot.core.handlers.games import game as handlers

        with patch.object(handlers, "UserRepository") as user_repo_cls, \
             patch.object(handlers, "GameRepository") as game_repo_cls, \
             patch.object(handlers, "DiscRepository") as disc_repo_cls, \
             patch.object(handlers, "QueueEntryRepository") as queue_repo_cls, \
             patch.object(handlers, "_can_enter_queue") as can_enter, \
             patch.object(handlers, "format_game_full") as format_full, \
             patch.object(handlers, "enter_queue_kb") as kb_factory, \
             patch.object(handlers, "get_entry_position") as get_pos:

            user_repo = AsyncMock()
            game_repo = AsyncMock()
            disc_repo = AsyncMock()
            queue_repo = AsyncMock()

            user_repo_cls.return_value = user_repo
            game_repo_cls.return_value = game_repo
            disc_repo_cls.return_value = disc_repo
            queue_repo_cls.return_value = queue_repo

            user = MagicMock(id=10, rentals=[], queues=[])
            game = MagicMock(id=1, title="Test Game", queues=[])
            user_repo.get_by_tg_id.return_value = user
            game_repo.get_by_id.return_value = game

            # Нет доступных дисков -> ставим в очередь
            disc_repo.get_available_discs_count_by_game.return_value = 0

            can_enter.return_value = None
            queue_repo.create_queue_entry.return_value = MagicMock()
            get_pos.return_value = 1
            format_full.return_value = "GAME_INFO"
            kb_factory.return_value = "KB"

            callback_data = GameCallback(
                game_id=1,
                action=GameAction.REQUEST_QUEUE,
            )

            await handlers.enter_game_queue(mock_callback_query, callback_data, test_session)

            user_repo.get_by_tg_id.assert_awaited_once_with(mock_callback_query.from_user.id)
            queue_repo.create_queue_entry.assert_awaited_once_with(user.id, game.id)
            assert mock_callback_query.answer.called

    @pytest.mark.asyncio
    async def test_take_game_user_not_registered(self, mock_callback_query, test_session):
        from game_share_bot.core.handlers.games import game as handlers

        with patch.object(handlers, "UserRepository") as user_repo_cls:
            user_repo = AsyncMock()
            user_repo_cls.return_value = user_repo

            user_repo.get_by_tg_id.return_value = None

            callback_data = GameCallback(
                game_id=1,
                action=GameAction.REQUEST_QUEUE,
            )

            await handlers.enter_game_queue(mock_callback_query, callback_data, test_session)

            assert mock_callback_query.answer.called
            msg = mock_callback_query.answer.call_args.args[0]
            assert "зарегистрироваться" in msg

    @pytest.mark.asyncio
    async def test_take_game_already_in_queue(self, mock_callback_query, test_session):
        from game_share_bot.core.handlers.games import game as handlers

        with patch.object(handlers, "UserRepository") as user_repo_cls, \
                patch.object(handlers, "GameRepository") as game_repo_cls, \
                patch.object(handlers, "_can_enter_queue") as can_enter:
            user_repo = AsyncMock()
            game_repo = AsyncMock()
            user_repo_cls.return_value = user_repo
            game_repo_cls.return_value = game_repo

            user = MagicMock(id=10, queues=[], rentals=[])
            user_repo.get_by_tg_id.return_value = user

            game_repo.get_by_id.return_value = MagicMock(id=1, title="Test Game")

            can_enter.return_value = "❌ Вы уже стоите в очереди за этой игрой"

            callback_data = GameCallback(
                game_id=1,
                action=GameAction.REQUEST_QUEUE,
            )

            await handlers.enter_game_queue(mock_callback_query, callback_data, test_session)

            mock_callback_query.answer.assert_called_once_with(
                "❌ Вы уже стоите в очереди за этой игрой"
            )

    @pytest.mark.asyncio
    async def test_take_game_no_available_discs(self, mock_callback_query, test_session):
        from game_share_bot.core.handlers.games import game as handlers

        with patch.object(handlers, "UserRepository") as user_repo_cls, \
             patch.object(handlers, "_can_enter_queue") as can_enter, \
             patch.object(handlers, "DiscRepository") as disc_repo_cls:

            user_repo = AsyncMock()
            disc_repo = AsyncMock()
            user_repo_cls.return_value = user_repo
            disc_repo_cls.return_value = disc_repo

            user = MagicMock(id=10, queues=[], rentals=[])
            user_repo.get_by_tg_id.return_value = user

            can_enter.return_value = None
            disc_repo.get_available_discs_count_by_game.return_value = 0

            callback_data = GameCallback(
                game_id=1,
                action=GameAction.REQUEST_QUEUE,
            )

            await handlers.enter_game_queue(mock_callback_query, callback_data, test_session)

            mock_callback_query.answer.assert_called_once()
            msg = mock_callback_query.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_take_game_game_not_found(self, mock_callback_query, test_session):
        from game_share_bot.core.handlers.games import game as handlers

        with patch.object(handlers, "UserRepository") as user_repo_cls, \
             patch.object(handlers, "_can_enter_queue") as can_enter, \
             patch.object(handlers, "GameRepository") as game_repo_cls:

            user_repo = AsyncMock()
            game_repo = AsyncMock()
            user_repo_cls.return_value = user_repo
            game_repo_cls.return_value = game_repo

            user = MagicMock(id=10, queues=[], rentals=[])
            user_repo.get_by_tg_id.return_value = user

            can_enter.return_value = None
            game_repo.get_by_id.return_value = None

            callback_data = GameCallback(
                game_id=999,
                action=GameAction.REQUEST_QUEUE,
            )

            await handlers.enter_game_queue(mock_callback_query, callback_data, test_session)

            mock_callback_query.answer.assert_called_once()
            msg = mock_callback_query.answer.call_args.args[0]
            assert "Игра не найдена" in msg
