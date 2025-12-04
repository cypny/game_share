"""
Тесты для функционала подтверждения взятия диска
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, User as TgUser

from game_share_bot.core.callbacks import RentalCallback, TakeDiscConfirmationCallback
from game_share_bot.core.handlers.user.queue import (
    request_take_disc_confirmation,
    confirm_take_disc,
    cancel_take_disc,
    my_queue
)
from game_share_bot.core.states import TakeDiscState
from game_share_bot.domain.enums import RentalStatus
from game_share_bot.infrastructure.models import Rental, User, Disc, Game


@pytest.fixture
def mock_callback():
    """Фикстура для создания mock callback query"""
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = MagicMock(spec=TgUser)
    callback.from_user.id = 123
    callback.message = AsyncMock()
    callback.answer = AsyncMock()
    return callback


@pytest.fixture
def mock_state():
    """Фикстура для создания mock FSM state"""
    state = AsyncMock(spec=FSMContext)
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    state.get_data = AsyncMock(return_value={"rental_id": 1})
    return state


@pytest.fixture
def mock_session():
    """Фикстура для создания mock database session"""
    return AsyncMock()


@pytest.fixture
def sample_rental():
    """Фикстура для создания примера аренды"""
    game = Game(id=1, title="Test Game")
    disc = Disc(disc_id=1, game_id=1, status_id=1)
    disc.game = game

    user = User(id=1, tg_id=123, phone="+1234567890", name="testuser")
    rental = Rental(
        id=1,
        user_id=1,
        disc_id=1,
        status_id=RentalStatus.PENDING_TAKE
    )
    rental.user = user
    rental.disc = disc
    return rental


class TestTakeDiscConfirmation:
    """Тесты для подтверждения взятия диска"""

    @pytest.mark.asyncio
    async def test_request_take_disc_confirmation_success(
        self, mock_callback, mock_session, mock_state, sample_rental
    ):
        """Тест успешного запроса подтверждения взятия диска"""
        callback_data = RentalCallback(action="take", rental_id=1)

        with patch('game_share_bot.core.handlers.user.queue.RentalRepository') as mock_rental_repo, \
             patch('game_share_bot.core.handlers.user.queue.UserRepository') as mock_user_repo:

            # Настройка моков
            rental_repo_instance = mock_rental_repo.return_value
            rental_repo_instance.get_by_id_with_relations = AsyncMock(return_value=sample_rental)

            user_repo_instance = mock_user_repo.return_value
            user_repo_instance.get_by_tg_id = AsyncMock(return_value=sample_rental.user)

            # Вызов функции
            await request_take_disc_confirmation(
                mock_callback, callback_data, mock_session, mock_state
            )

            # Проверки
            assert mock_state.update_data.called
            assert mock_state.set_state.called
            mock_state.set_state.assert_called_once_with(TakeDiscState.waiting_for_confirmation)
            mock_callback.message.edit_text.assert_called_once()

            # Проверяем, что текст сообщения содержит название игры
            call_args = mock_callback.message.edit_text.call_args
            call_kwargs = call_args.kwargs if call_args.kwargs else call_args[1] if len(call_args) > 1 else {}
            text = call_kwargs.get('text', call_args[0][0] if call_args and len(call_args[0]) > 0 else '')
            assert "Test Game" in text
            assert "Вы точно взяли диск?" in text

    @pytest.mark.asyncio
    async def test_request_take_disc_confirmation_rental_not_found(
        self, mock_callback, mock_session, mock_state
    ):
        """Тест запроса подтверждения для несуществующей аренды"""
        callback_data = RentalCallback(action="take", rental_id=999)

        with patch('game_share_bot.core.handlers.user.queue.RentalRepository') as mock_rental_repo:
            rental_repo_instance = mock_rental_repo.return_value
            rental_repo_instance.get_by_id_with_relations = AsyncMock(return_value=None)

            await request_take_disc_confirmation(
                mock_callback, callback_data, mock_session, mock_state
            )

            mock_callback.answer.assert_called_once_with("❌ Аренда не найдена")

    @pytest.mark.asyncio
    async def test_confirm_take_disc_success(
        self, mock_callback, mock_session, mock_state, sample_rental
    ):
        """Тест успешного подтверждения взятия диска"""
        callback_data = TakeDiscConfirmationCallback(rental_id=1, is_confirmed=True)

        with patch('game_share_bot.core.handlers.user.queue.RentalRepository') as mock_rental_repo, \
             patch('game_share_bot.core.handlers.user.queue.my_queue') as mock_my_queue:

            rental_repo_instance = mock_rental_repo.return_value
            rental_repo_instance.get_by_id_with_relations = AsyncMock(return_value=sample_rental)
            rental_repo_instance.confirm_take = AsyncMock(return_value=True)

            await confirm_take_disc(
                mock_callback, callback_data, mock_session, mock_state
            )

            # Проверки
            rental_repo_instance.confirm_take.assert_called_once_with(1)
            mock_callback.answer.assert_called_once_with("✅ Вы успешно взяли диск!")
            mock_state.clear.assert_called()
            mock_my_queue.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_take_disc_failed(
        self, mock_callback, mock_session, mock_state, sample_rental
    ):
        """Тест неудачного подтверждения взятия диска"""
        callback_data = TakeDiscConfirmationCallback(rental_id=1, is_confirmed=True)

        with patch('game_share_bot.core.handlers.user.queue.RentalRepository') as mock_rental_repo:
            rental_repo_instance = mock_rental_repo.return_value
            rental_repo_instance.get_by_id_with_relations = AsyncMock(return_value=sample_rental)
            rental_repo_instance.confirm_take = AsyncMock(return_value=False)

            await confirm_take_disc(
                mock_callback, callback_data, mock_session, mock_state
            )

            mock_callback.answer.assert_called_once_with("❌ Ошибка при взятии")
            mock_state.clear.assert_called()

    @pytest.mark.asyncio
    async def test_cancel_take_disc(
        self, mock_callback, mock_session, mock_state
    ):
        """Тест отмены взятия диска"""
        callback_data = TakeDiscConfirmationCallback(rental_id=1, is_confirmed=False)

        with patch('game_share_bot.core.handlers.user.queue.my_queue') as mock_my_queue:
            await cancel_take_disc(
                mock_callback, callback_data, mock_session, mock_state
            )

            mock_callback.answer.assert_called_once_with("❌ Взятие диска отменено")
            mock_state.clear.assert_called()
            mock_my_queue.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_take_disc_confirmation_wrong_status(
        self, mock_callback, mock_session, mock_state, sample_rental
    ):
        """Тест запроса подтверждения для аренды с неправильным статусом"""
        callback_data = RentalCallback(action="take", rental_id=1)
        sample_rental.status_id = RentalStatus.ACTIVE  # Неправильный статус

        with patch('game_share_bot.core.handlers.user.queue.RentalRepository') as mock_rental_repo, \
             patch('game_share_bot.core.handlers.user.queue.UserRepository') as mock_user_repo:

            rental_repo_instance = mock_rental_repo.return_value
            rental_repo_instance.get_by_id_with_relations = AsyncMock(return_value=sample_rental)

            user_repo_instance = mock_user_repo.return_value
            user_repo_instance.get_by_tg_id = AsyncMock(return_value=sample_rental.user)

            await request_take_disc_confirmation(
                mock_callback, callback_data, mock_session, mock_state
            )

            mock_callback.answer.assert_called_once_with("❌ Диск уже взят или возвращен")

