import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from game_share_bot.core.callbacks import GameCallback
from game_share_bot.domain.enums.actions.game_actions import GameAction


class TestTakeGameHandlers:
    @pytest.mark.asyncio
    async def test_take_game_success(self, mock_callback_query, test_session, mock_state):
        from game_share_bot.core.handlers.games import game as handlers

        # Мокаем session.refresh
        test_session.refresh = AsyncMock()
        test_session.flush = AsyncMock()

        with patch.object(handlers, "UserRepository") as user_repo_cls, \
             patch.object(handlers, "GameRepository") as game_repo_cls, \
             patch.object(handlers, "DiscRepository") as disc_repo_cls, \
             patch.object(handlers, "QueueEntryRepository") as queue_repo_cls, \
             patch.object(handlers, "RentalRepository") as rental_repo_cls, \
             patch.object(handlers, "_can_enter_queue") as can_enter, \
             patch.object(handlers, "_get_game_status_info") as get_status_info, \
             patch.object(handlers, "format_game_full") as format_full, \
             patch.object(handlers, "enter_queue_kb") as kb_factory, \
             patch.object(handlers, "get_entry_position") as get_pos, \
             patch.object(handlers, "update_queue_to_rental_internal") as update_queue:

            user_repo = AsyncMock()
            game_repo = AsyncMock()
            disc_repo = AsyncMock()
            queue_repo = AsyncMock()
            rental_repo = AsyncMock()

            user_repo_cls.return_value = user_repo
            game_repo_cls.return_value = game_repo
            disc_repo_cls.return_value = disc_repo
            queue_repo_cls.return_value = queue_repo
            rental_repo_cls.return_value = rental_repo

            user = MagicMock(id=10, rentals=[], queues=[])
            game = MagicMock(id=1, title="Test Game", queues=[])
            available_disc = MagicMock()

            user_repo.get_by_tg_id.return_value = user
            game_repo.get_by_id.return_value = game
            disc_repo.get_available_disc_by_game.return_value = available_disc

            # Нет доступных дисков -> ставим в очередь
            disc_repo.get_available_discs_count_by_game.return_value = 0

            can_enter.return_value = None
            queue_repo.create_queue_entry.return_value = MagicMock()
            get_pos.return_value = 1
            get_status_info.return_value = MagicMock()
            format_full.return_value = "GAME_INFO"
            kb_factory.return_value = "KB"

            callback_data = GameCallback(
                game_id=1,
                action=GameAction.REQUEST_QUEUE,
            )

            await handlers.enter_game_queue(mock_callback_query, callback_data, test_session, mock_state)

            user_repo.get_by_tg_id.assert_awaited_once_with(mock_callback_query.from_user.id)
            queue_repo.create_queue_entry.assert_awaited_once_with(user.id, game.id)
            assert mock_callback_query.answer.called

    @pytest.mark.asyncio
    async def test_take_game_user_not_registered(self, mock_callback_query, test_session, mock_state):
        from game_share_bot.core.handlers.games import game as handlers

        with patch.object(handlers, "UserRepository") as user_repo_cls:
            user_repo = AsyncMock()
            user_repo_cls.return_value = user_repo

            user_repo.get_by_tg_id.return_value = None

            callback_data = GameCallback(
                game_id=1,
                action=GameAction.REQUEST_QUEUE,
            )

            await handlers.enter_game_queue(mock_callback_query, callback_data, test_session, mock_state)

            assert mock_callback_query.answer.called
            msg = mock_callback_query.answer.call_args.args[0]
            assert "зарегистрироваться" in msg

    @pytest.mark.asyncio
    async def test_take_game_already_in_queue(self, mock_callback_query, test_session, mock_state):
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

            await handlers.enter_game_queue(mock_callback_query, callback_data, test_session, mock_state)

            mock_callback_query.answer.assert_called_once_with(
                "❌ Вы уже стоите в очереди за этой игрой"
            )

    @pytest.mark.asyncio
    async def test_take_game_no_available_discs(self, mock_callback_query, test_session, mock_state):
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
            disc_repo.get_available_disc_by_game.return_value = None

            callback_data = GameCallback(
                game_id=1,
                action=GameAction.REQUEST_QUEUE,
            )

            await handlers.enter_game_queue(mock_callback_query, callback_data, test_session, mock_state)

            mock_callback_query.answer.assert_called_once()
            msg = mock_callback_query.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_take_game_game_not_found(self, mock_callback_query, test_session, mock_state):
        from game_share_bot.core.handlers.games import game as handlers

        with patch.object(handlers, "UserRepository") as user_repo_cls, \
             patch.object(handlers, "_can_enter_queue") as can_enter, \
             patch.object(handlers, "GameRepository") as game_repo_cls, \
             patch.object(handlers, "DiscRepository") as disc_repo_cls:

            user_repo = AsyncMock()
            game_repo = AsyncMock()
            disc_repo = AsyncMock()
            user_repo_cls.return_value = user_repo
            game_repo_cls.return_value = game_repo
            disc_repo_cls.return_value = disc_repo

            user = MagicMock(id=10, queues=[], rentals=[])
            available_disc = MagicMock()
            user_repo.get_by_tg_id.return_value = user
            disc_repo.get_available_disc_by_game.return_value = available_disc

            can_enter.return_value = None
            game_repo.get_by_id.return_value = None

            callback_data = GameCallback(
                game_id=999,
                action=GameAction.REQUEST_QUEUE,
            )

            await handlers.enter_game_queue(mock_callback_query, callback_data, test_session, mock_state)

            mock_callback_query.answer.assert_called_once()
            msg = mock_callback_query.answer.call_args.args[0]
            assert "Игра не найдена" in msg

    @pytest.mark.asyncio
    async def test_take_game_first_in_queue_shows_confirmation(self, mock_callback_query, test_session, mock_state):
        """Тест: если пользователь становится первым в очереди, показывается окно подтверждения"""
        from game_share_bot.core.handlers.games import game as handlers
        from game_share_bot.domain.enums import RentalStatus

        # Мокаем session.refresh
        test_session.refresh = AsyncMock()
        test_session.flush = AsyncMock()

        with patch.object(handlers, "UserRepository") as user_repo_cls, \
             patch.object(handlers, "GameRepository") as game_repo_cls, \
             patch.object(handlers, "DiscRepository") as disc_repo_cls, \
             patch.object(handlers, "QueueEntryRepository") as queue_repo_cls, \
             patch.object(handlers, "RentalRepository") as rental_repo_cls, \
             patch.object(handlers, "_can_enter_queue") as can_enter, \
             patch.object(handlers, "update_queue_to_rental_internal") as update_queue, \
             patch.object(handlers, "_get_game_status_info") as get_status_info, \
             patch.object(handlers, "format_game_full") as format_full, \
             patch.object(handlers, "enter_queue_kb") as kb_factory:

            user_repo = AsyncMock()
            game_repo = AsyncMock()
            disc_repo = AsyncMock()
            queue_repo = AsyncMock()
            rental_repo = AsyncMock()

            user_repo_cls.return_value = user_repo
            game_repo_cls.return_value = game_repo
            disc_repo_cls.return_value = disc_repo
            queue_repo_cls.return_value = queue_repo
            rental_repo_cls.return_value = rental_repo

            # Создаем rental который будет создан при update_queue_to_rental_internal
            mock_disc = MagicMock(game_id=1)
            mock_rental = MagicMock(id=100, disc=mock_disc, status_id=RentalStatus.PENDING_TAKE)

            user = MagicMock(id=10, rentals=[mock_rental], queues=[])
            game = MagicMock(id=1, title="Test Game", queues=[])
            available_disc = MagicMock()

            user_repo.get_by_tg_id.return_value = user
            game_repo.get_by_id.return_value = game
            disc_repo.get_available_disc_by_game.return_value = available_disc
            can_enter.return_value = None
            queue_repo.create_queue_entry.return_value = MagicMock()
            get_status_info.return_value = MagicMock()
            format_full.return_value = "GAME_INFO"
            kb_factory.return_value = "KB"

            callback_data = GameCallback(
                game_id=1,
                action=GameAction.REQUEST_QUEUE,
            )

            await handlers.enter_game_queue(mock_callback_query, callback_data, test_session, mock_state)

            # Проверяем, что состояние было установлено
            mock_state.update_data.assert_called_once_with(rental_id=100)
            mock_state.set_state.assert_called_once()

            # Проверяем, что было отправлено сообщение с подтверждением
            assert mock_callback_query.message.answer.called
            call_args = mock_callback_query.message.answer.call_args
            text = call_args[0][0] if call_args[0] else call_args.kwargs.get('text', '')
            assert "Test Game" in text
            assert "Вы точно взяли диск?" in text

    @pytest.mark.asyncio
    async def test_take_game_not_first_in_queue_no_confirmation(self, mock_callback_query, test_session, mock_state):
        """Тест: если пользователь не первый в очереди, окно подтверждения не показывается"""
        from game_share_bot.core.handlers.games import game as handlers
        from game_share_bot.domain.enums import RentalStatus

        # Мокаем session.refresh
        test_session.refresh = AsyncMock()
        test_session.flush = AsyncMock()

        with patch.object(handlers, "UserRepository") as user_repo_cls, \
             patch.object(handlers, "GameRepository") as game_repo_cls, \
             patch.object(handlers, "DiscRepository") as disc_repo_cls, \
             patch.object(handlers, "QueueEntryRepository") as queue_repo_cls, \
             patch.object(handlers, "RentalRepository") as rental_repo_cls, \
             patch.object(handlers, "_can_enter_queue") as can_enter, \
             patch.object(handlers, "update_queue_to_rental_internal") as update_queue, \
             patch.object(handlers, "_get_game_status_info") as get_status_info, \
             patch.object(handlers, "format_game_full") as format_full, \
             patch.object(handlers, "enter_queue_kb") as kb_factory:

            user_repo = AsyncMock()
            game_repo = AsyncMock()
            disc_repo = AsyncMock()
            queue_repo = AsyncMock()
            rental_repo = AsyncMock()

            user_repo_cls.return_value = user_repo
            game_repo_cls.return_value = game_repo
            disc_repo_cls.return_value = disc_repo
            queue_repo_cls.return_value = queue_repo
            rental_repo_cls.return_value = rental_repo

            # НЕ создаем rental - пользователь не первый в очереди
            user = MagicMock(id=10, rentals=[], queues=[])
            game = MagicMock(id=1, title="Test Game", queues=[])
            available_disc = MagicMock()

            user_repo.get_by_tg_id.return_value = user
            game_repo.get_by_id.return_value = game
            disc_repo.get_available_disc_by_game.return_value = available_disc
            can_enter.return_value = None
            queue_repo.create_queue_entry.return_value = MagicMock()
            get_status_info.return_value = MagicMock()
            format_full.return_value = "GAME_INFO"
            kb_factory.return_value = "KB"

            callback_data = GameCallback(
                game_id=1,
                action=GameAction.REQUEST_QUEUE,
            )

            await handlers.enter_game_queue(mock_callback_query, callback_data, test_session, mock_state)

            # Проверяем, что состояние НЕ было установлено
            mock_state.update_data.assert_not_called()
            mock_state.set_state.assert_not_called()

            # Проверяем, что было показано обычное сообщение об успехе
            mock_callback_query.answer.assert_called()
            msg = mock_callback_query.answer.call_args.args[0]
            assert "встали в очередь" in msg
