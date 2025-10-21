import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from aiogram.types import CallbackQuery

from game_share_bot.domain.enums import DiscStatus


class TestTakeGameHandlers:
    """Тесты для процесса взятия игры"""

    @pytest.mark.asyncio
    async def test_take_game_success(self, mock_callback_query, test_session):
        """Тест успешного взятия игры"""
        with patch('game_share_bot.core.handlers.games.catalog.GameRepository') as mock_game_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.DiscRepository') as mock_disc_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.RentalRepository') as mock_rental_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.UserRepository') as mock_user_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.get_game_detail_kb') as mock_kb:
            # Настраиваем моки
            mock_game_repo = AsyncMock()
            mock_disc_repo = AsyncMock()
            mock_rental_repo = AsyncMock()
            mock_user_repo = AsyncMock()

            mock_game_repo_class.return_value = mock_game_repo
            mock_disc_repo_class.return_value = mock_disc_repo
            mock_rental_repo_class.return_value = mock_rental_repo
            mock_user_repo_class.return_value = mock_user_repo

            # Настраиваем данные
            test_user = MagicMock(id=1)
            mock_user_repo.get_by_tg_id.return_value = test_user

            test_game = MagicMock(id=1, title="Test Game")
            mock_game_repo.get_by_id.return_value = test_game

            # Нет активной аренды
            mock_rental_repo.get_active_rental_by_user_and_game.return_value = None

            # Есть доступный диск
            test_disc = MagicMock(disc_id=123)
            mock_disc_repo.get_available_disc_by_game.return_value = test_disc

            # Успешное создание аренды
            test_rental = MagicMock(id=456)
            mock_rental_repo.create_rental.return_value = test_rental

            # Успешное обновление статуса диска
            mock_disc_repo.update_disc_status.return_value = True

            # После взятия осталось 1 диск
            mock_disc_repo.get_available_discs_count_by_game.return_value = 1

            mock_kb.return_value = "mock_updated_keyboard"

            # Устанавливаем callback data
            mock_callback_query.data = "take_game_1"
            mock_callback_query.message.photo = [MagicMock()]  # Сообщение с фото

            from game_share_bot.core.handlers.games.catalog import take_game
            await take_game(mock_callback_query, test_session)

            # Проверяем вызовы
            mock_user_repo.get_by_tg_id.assert_called_with(mock_callback_query.from_user.id)
            mock_rental_repo.get_active_rental_by_user_and_game.assert_called_with(1, 1)
            mock_disc_repo.get_available_disc_by_game.assert_called_with(1)
            mock_rental_repo.create_rental.assert_called_with(1, 123)
            mock_disc_repo.update_disc_status.assert_called_with(123, DiscStatus.RENTED)

            # Проверяем ответ пользователю
            mock_callback_query.answer.assert_called_with("✅ Вы успешно взяли игру 'Test Game'!")

            # Проверяем обновление сообщения
            mock_callback_query.message.edit_caption.assert_called_once()
            call_args = mock_callback_query.message.edit_caption.call_args
            assert "Вы уже взяли эту игру" in call_args[1]['caption']
            assert "Осталось дисков: 1" in call_args[1]['caption']
            assert call_args[1]['reply_markup'] == "mock_updated_keyboard"

    @pytest.mark.asyncio
    async def test_take_game_user_not_registered(self, mock_callback_query, test_session):
        """Тест когда пользователь не зарегистрирован"""
        with patch('game_share_bot.core.handlers.games.catalog.UserRepository') as mock_user_repo_class:
            mock_user_repo = AsyncMock()
            mock_user_repo_class.return_value = mock_user_repo
            mock_user_repo.get_by_tg_id.return_value = None

            mock_callback_query.data = "take_game_1"

            from game_share_bot.core.handlers.games.catalog import take_game
            await take_game(mock_callback_query, test_session)

            mock_callback_query.answer.assert_called_with("❌ Сначала нужно зарегистрироваться")

    @pytest.mark.asyncio
    async def test_take_game_already_rented(self, mock_callback_query, test_session):
        """Тест когда у пользователя уже есть активная аренда"""
        with patch('game_share_bot.core.handlers.games.catalog.UserRepository') as mock_user_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.RentalRepository') as mock_rental_repo_class:
            mock_user_repo = AsyncMock()
            mock_rental_repo = AsyncMock()

            mock_user_repo_class.return_value = mock_user_repo
            mock_rental_repo_class.return_value = mock_rental_repo

            test_user = MagicMock(id=1)
            mock_user_repo.get_by_tg_id.return_value = test_user

            # У пользователя уже есть активная аренда
            mock_rental_repo.get_active_rental_by_user_and_game.return_value = MagicMock()

            mock_callback_query.data = "take_game_1"

            from game_share_bot.core.handlers.games.catalog import take_game
            await take_game(mock_callback_query, test_session)

            mock_callback_query.answer.assert_called_with("❌ У вас уже есть эта игра на руках")

    @pytest.mark.asyncio
    async def test_take_game_no_available_discs(self, mock_callback_query, test_session):
        """Тест когда нет доступных дисков"""
        with patch('game_share_bot.core.handlers.games.catalog.UserRepository') as mock_user_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.RentalRepository') as mock_rental_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.DiscRepository') as mock_disc_repo_class:
            mock_user_repo = AsyncMock()
            mock_rental_repo = AsyncMock()
            mock_disc_repo = AsyncMock()

            mock_user_repo_class.return_value = mock_user_repo
            mock_rental_repo_class.return_value = mock_rental_repo
            mock_disc_repo_class.return_value = mock_disc_repo

            test_user = MagicMock(id=1)
            mock_user_repo.get_by_tg_id.return_value = test_user
            mock_rental_repo.get_active_rental_by_user_and_game.return_value = None
            mock_disc_repo.get_available_disc_by_game.return_value = None  # Нет доступных дисков

            mock_callback_query.data = "take_game_1"

            from game_share_bot.core.handlers.games.catalog import take_game
            await take_game(mock_callback_query, test_session)

            mock_callback_query.answer.assert_called_with("❌ Все диски этой игры заняты")

    @pytest.mark.asyncio
    async def test_take_game_game_not_found(self, mock_callback_query, test_session):
        """Тест когда игра не найдена"""
        with patch('game_share_bot.core.handlers.games.catalog.UserRepository') as mock_user_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.RentalRepository') as mock_rental_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.DiscRepository') as mock_disc_repo_class, \
                patch('game_share_bot.core.handlers.games.catalog.GameRepository') as mock_game_repo_class:
            mock_user_repo = AsyncMock()
            mock_rental_repo = AsyncMock()
            mock_disc_repo = AsyncMock()
            mock_game_repo = AsyncMock()

            mock_user_repo_class.return_value = mock_user_repo
            mock_rental_repo_class.return_value = mock_rental_repo
            mock_disc_repo_class.return_value = mock_disc_repo
            mock_game_repo_class.return_value = mock_game_repo

            test_user = MagicMock(id=1)
            mock_user_repo.get_by_tg_id.return_value = test_user
            mock_rental_repo.get_active_rental_by_user_and_game.return_value = None

            test_disc = MagicMock(disc_id=123)
            mock_disc_repo.get_available_disc_by_game.return_value = test_disc

            # Игра не найдена
            mock_game_repo.get_by_id.return_value = None

            mock_callback_query.data = "take_game_1"

            from game_share_bot.core.handlers.games.catalog import take_game
            await take_game(mock_callback_query, test_session)

            mock_callback_query.answer.assert_called_with("❌ Игра не найдена")