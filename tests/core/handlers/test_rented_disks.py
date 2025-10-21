import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import RentalCallback, MenuCallback
from game_share_bot.domain.enums import MenuSection, RentalStatus, DiscStatus
from game_share_bot.infrastructure.models import Rental, Disc, Game, User as UserModel


class TestRentedDisksHandlers:
    """Тесты для хендлеров арендованных дисков"""

    @pytest.fixture
    def mock_rental(self):
        """Создает мок аренды для тестов"""
        game = Game(id=1, title="Test Game", description="Test Description")
        disc = Disc(disc_id=1, game_id=1, status_id=DiscStatus.RENTED)
        disc.game = game

        user = UserModel(id=1, tg_id=123, phone="+79991234567", name="Test User")

        rental = Rental(
            id=1,
            user_id=1,
            disc_id=1,
            status_id=RentalStatus.ACTIVE,
            start_date=datetime(2024, 1, 1),
            expected_end_date=datetime(2024, 1, 31),
            actual_end_date=None
        )
        rental.disc = disc
        rental.user = user

        return rental

    @pytest.mark.asyncio
    async def test_show_rented_disks_with_rentals(self, test_session, mock_callback_query, mock_rental):
        """Тест показа арендованных дисков когда они есть"""
        from game_share_bot.core.handlers.menu.rented_disks import show_rented_disks

        rental_repo = AsyncMock()
        rental_repo.get_active_rentals_by_user = AsyncMock(return_value=[mock_rental])

        with patch('game_share_bot.core.handlers.menu.rented_disks.RentalRepository', return_value=rental_repo):
            await show_rented_disks(mock_callback_query, test_session)

        # Проверяем, что сообщение было отредактировано
        mock_callback_query.message.edit_text.assert_called_once()

        # Проверяем содержимое сообщения
        call_args = mock_callback_query.message.edit_text.call_args
        text = call_args[0][0]
        assert "📦 Ваши арендованные диски:" in text
        assert "Test Game" in text
        assert "01.01.2024" in text  # start_date
        assert "31.01.2024" in text  # expected_end_date

    @pytest.mark.asyncio
    async def test_show_rented_disks_empty(self, test_session, mock_callback_query):
        """Тест показа арендованных дисков когда их нет"""
        from game_share_bot.core.handlers.menu.rented_disks import show_rented_disks

        rental_repo = AsyncMock()
        rental_repo.get_active_rentals_by_user = AsyncMock(return_value=[])

        with patch('game_share_bot.core.handlers.menu.rented_disks.RentalRepository', return_value=rental_repo):
            await show_rented_disks(mock_callback_query, test_session)

        # Проверяем сообщение о пустом списке
        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args
        assert "📦 У вас нет арендованных дисков" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_show_rented_disks_exception(self, test_session, mock_callback_query):
        """Тест обработки исключения при показе арендованных дисков"""
        from game_share_bot.core.handlers.menu.rented_disks import show_rented_disks

        rental_repo = AsyncMock()
        rental_repo.get_active_rentals_by_user = AsyncMock(side_effect=Exception("DB error"))

        with patch('game_share_bot.core.handlers.menu.rented_disks.RentalRepository', return_value=rental_repo):
            await show_rented_disks(mock_callback_query, test_session)

        # Проверяем, что был вызван answer с ошибкой
        mock_callback_query.answer.assert_called_once_with("❌ Ошибка при загрузке списка дисков")

    @pytest.mark.asyncio
    async def test_return_disk_success(self, test_session, mock_callback_query, mock_rental):
        """Тест успешного запроса на возврат диска"""
        from game_share_bot.core.handlers.menu.rented_disks import return_disk

        # Создаем callback данные
        callback_data = RentalCallback(action="return", rental_id=1)

        # Мокаем репозитории
        rental_repo = AsyncMock()
        rental_repo.get_by_id_with_relations = AsyncMock(return_value=mock_rental)
        rental_repo.get_by_id_with_disc = AsyncMock(return_value=mock_rental)
        rental_repo.update_rental_status = AsyncMock(return_value=True)

        disc_repo = AsyncMock()
        disc_repo.update_disc_status = AsyncMock(return_value=True)

        # Мокаем show_rented_disks чтобы проверить, что он вызывается после успешного возврата
        with patch('game_share_bot.core.handlers.menu.rented_disks.RentalRepository', return_value=rental_repo), \
                patch('game_share_bot.core.handlers.menu.rented_disks.DiscRepository', return_value=disc_repo), \
                patch('game_share_bot.core.handlers.menu.rented_disks.show_rented_disks') as mock_show:
            await return_disk(mock_callback_query, callback_data, test_session)

        # Проверяем, что был вызван answer с успехом
        mock_callback_query.answer.assert_called_once_with(
            "⏳ Запрос на возврат диска 'Test Game' отправлен администратору!")

        # Проверяем, что был вызван show_rented_disks для обновления списка
        mock_show.assert_called_once_with(mock_callback_query, test_session)

        # Проверяем, что статусы были обновлены
        rental_repo.update_rental_status.assert_called_once_with(1, RentalStatus.PENDING_RETURN)
        disc_repo.update_disc_status.assert_called_once_with(1, DiscStatus.PENDING_RETURN)

    @pytest.mark.asyncio
    async def test_return_disk_rental_not_found(self, test_session, mock_callback_query):
        """Тест возврата несуществующей аренды"""
        from game_share_bot.core.handlers.menu.rented_disks import return_disk

        callback_data = RentalCallback(action="return", rental_id=999)

        rental_repo = AsyncMock()
        rental_repo.get_by_id_with_relations = AsyncMock(return_value=None)

        with patch('game_share_bot.core.handlers.menu.rented_disks.RentalRepository', return_value=rental_repo):
            await return_disk(mock_callback_query, callback_data, test_session)

        # Проверяем, что был вызван answer с ошибкой
        mock_callback_query.answer.assert_called_once_with("❌ Аренда не найдена")

    @pytest.mark.asyncio
    async def test_return_disk_not_user_rental(self, test_session, mock_callback_query, mock_rental):
        """Тест возврата диска, который не принадлежит пользователю"""
        from game_share_bot.core.handlers.menu.rented_disks import return_disk

        callback_data = RentalCallback(action="return", rental_id=1)

        # Меняем tg_id пользователя в аренде
        mock_rental.user.tg_id = 999  # Другой пользователь

        rental_repo = AsyncMock()
        rental_repo.get_by_id_with_relations = AsyncMock(return_value=mock_rental)

        with patch('game_share_bot.core.handlers.menu.rented_disks.RentalRepository', return_value=rental_repo):
            await return_disk(mock_callback_query, callback_data, test_session)

        # Проверяем, что был вызван answer с ошибкой
        mock_callback_query.answer.assert_called_once_with("❌ Это не ваш диск")

    @pytest.mark.asyncio
    async def test_return_disk_update_failed(self, test_session, mock_callback_query, mock_rental):
        """Тест когда обновление статуса возврата не удалось"""
        from game_share_bot.core.handlers.menu.rented_disks import return_disk

        callback_data = RentalCallback(action="return", rental_id=1)

        rental_repo = AsyncMock()
        rental_repo.get_by_id_with_relations = AsyncMock(return_value=mock_rental)
        rental_repo.get_by_id_with_disc = AsyncMock(return_value=mock_rental)
        rental_repo.update_rental_status = AsyncMock(return_value=False)  # Ошибка обновления

        disc_repo = AsyncMock()
        disc_repo.update_disc_status = AsyncMock(return_value=True)

        with patch('game_share_bot.core.handlers.menu.rented_disks.RentalRepository', return_value=rental_repo), \
                patch('game_share_bot.core.handlers.menu.rented_disks.DiscRepository', return_value=disc_repo):
            await return_disk(mock_callback_query, callback_data, test_session)

        # Проверяем, что был вызван answer с ошибкой
        mock_callback_query.answer.assert_called_once_with("❌ Ошибка при запросе возврата диска")

    @pytest.mark.asyncio
    async def test_return_disk_exception(self, test_session, mock_callback_query):
        """Тест обработки исключения при возврате диска"""
        from game_share_bot.core.handlers.menu.rented_disks import return_disk

        callback_data = RentalCallback(action="return", rental_id=1)

        rental_repo = AsyncMock()
        rental_repo.get_by_id_with_relations = AsyncMock(side_effect=Exception("DB error"))

        with patch('game_share_bot.core.handlers.menu.rented_disks.RentalRepository', return_value=rental_repo):
            await return_disk(mock_callback_query, callback_data, test_session)

        # Проверяем, что был вызван answer с ошибкой
        mock_callback_query.answer.assert_called_once_with("❌ Ошибка при запросе возврата диска")

    @pytest.mark.asyncio
    async def test_format_rented_disks_message(self):
        """Тест форматирования сообщения об арендованных дисках"""
        from game_share_bot.core.handlers.menu.rented_disks import _format_rented_disks_message

        # Тест с пустым списком
        empty_message = _format_rented_disks_message([])
        assert empty_message == "📦 У вас нет арендованных дисков"

        # Тест с одной арендой
        game = Game(title="Game 1")
        disc = Disc(game=game)
        rental = Rental(
            disc=disc,
            start_date=datetime(2024, 1, 1),
            expected_end_date=datetime(2024, 1, 31),
            status_id=RentalStatus.ACTIVE
        )

        message = _format_rented_disks_message([rental])
        assert "Game 1" in message
        assert "01.01.2024" in message
        assert "31.01.2024" in message

        # Тест с арендой в статусе ожидания возврата
        rental_pending = Rental(
            disc=disc,
            start_date=datetime(2024, 1, 1),
            expected_end_date=datetime(2024, 1, 31),
            status_id=RentalStatus.PENDING_RETURN
        )

        message_pending = _format_rented_disks_message([rental_pending])
        assert "Ожидает подтверждения возврата администратором" in message_pending

    @pytest.mark.asyncio
    async def test_validate_rental_return_success(self, test_session, mock_rental):
        """Тест успешной валидации возврата аренды"""
        from game_share_bot.core.handlers.menu.rented_disks import _validate_rental_return

        rental_repo = AsyncMock()
        rental_repo.get_by_id_with_relations = AsyncMock(return_value=mock_rental)

        with patch('game_share_bot.core.handlers.menu.rented_disks.RentalRepository', return_value=rental_repo):
            is_valid, game_title = await _validate_rental_return(1, 123, test_session)

        assert is_valid is True
        assert game_title == "Test Game"

    @pytest.mark.asyncio
    async def test_process_disk_return_success(self, test_session, mock_rental):
        """Тест успешной обработки возврата диска"""
        from game_share_bot.core.handlers.menu.rented_disks import _process_disk_return

        rental_repo = AsyncMock()
        rental_repo.get_by_id_with_disc = AsyncMock(return_value=mock_rental)
        rental_repo.update_rental_status = AsyncMock(return_value=True)

        disc_repo = AsyncMock()
        disc_repo.update_disc_status = AsyncMock(return_value=True)

        with patch('game_share_bot.core.handlers.menu.rented_disks.RentalRepository', return_value=rental_repo), \
                patch('game_share_bot.core.handlers.menu.rented_disks.DiscRepository', return_value=disc_repo):
            result = await _process_disk_return(1, test_session)

        assert result is True
        rental_repo.update_rental_status.assert_called_once_with(1, RentalStatus.PENDING_RETURN)
        disc_repo.update_disc_status.assert_called_once_with(1, DiscStatus.PENDING_RETURN)