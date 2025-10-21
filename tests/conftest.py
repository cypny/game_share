import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, CallbackQuery, User, Contact
from sqlalchemy.ext.asyncio import AsyncSession

from tests.infrastructure.database import init_test_db, get_test_session, test_db
from game_share_bot.infrastructure.models.base import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_database():
    """Инициализация тестовой БД на всю сессию тестов"""
    db = await init_test_db()
    yield db
    await db.dispose()


@pytest.fixture
async def test_session(test_database):
    """Создание новой сессии для каждого теста"""
    session = test_database.session_factory()

    try:
        yield session
    finally:
        await session.close()


@pytest.fixture
async def mock_session(test_session):
    """Замена мок-сессии на реальную тестовую сессию БД"""
    return test_session


@pytest.fixture
def mock_message():
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock(spec=User)
    message.from_user.id = 123
    message.from_user.full_name = "Test User"
    message.from_user.username = "testuser"
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    return message


@pytest.fixture
def mock_callback_query():
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = AsyncMock(spec=User)
    callback.from_user.id = 123
    callback.from_user.full_name = "Test User"
    callback.from_user.username = "testuser"
    callback.message = AsyncMock(spec=Message)
    callback.message.edit_text = AsyncMock()
    callback.message.edit_caption = AsyncMock()
    callback.answer = AsyncMock()
    return callback


@pytest.fixture
def mock_message_with_contact():
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock(spec=User)
    message.from_user.id = 123
    message.from_user.full_name = "Test User"
    message.from_user.username = "testuser"
    message.contact = AsyncMock(spec=Contact)
    message.contact.phone_number = "+1234567890"
    message.answer = AsyncMock()
    return message


@pytest.fixture
def mock_state():
    state = AsyncMock()
    state.clear = AsyncMock()
    state.set_state = AsyncMock()
    return state


@pytest.fixture
def rental_callback_data():
    """Фикстура для создания callback данных аренды"""
    def _create(action="return", rental_id=1):
        return MagicMock(action=action, rental_id=rental_id)
    return _create


# Фикстуры для тестовых данных
@pytest.fixture
async def test_user(test_session):
    """Создание тестового пользователя"""
    from game_share_bot.infrastructure.repositories.user import UserRepository

    repo = UserRepository(test_session)
    user = await repo.try_create(
        tg_id=123,
        phone="+1234567890",
        name="Test User"
    )
    return user


@pytest.fixture
async def test_game(test_session):
    """Создание тестовой игры"""
    from game_share_bot.infrastructure.repositories.game import GameRepository

    repo = GameRepository(test_session)
    game = await repo.create(
        title="Test Game",
        description="Test Description",
        cover_image_url="test_image.jpg"
    )
    return game


@pytest.fixture(autouse=True)
async def clean_database(test_session):
    """Автоматическая очистка базы данных перед каждым тестом"""
    # Удаляем все данные из таблиц, кроме системных статусов
    for table in reversed(Base.metadata.sorted_tables):
        if table.name not in ['discs_status', 'rental_statuses']:
            await test_session.execute(table.delete())
    await test_session.commit()