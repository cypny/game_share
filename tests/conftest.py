import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4
from aiogram.types import Message, CallbackQuery, User as TgUser, Contact
from sqlalchemy.ext.asyncio import AsyncSession

from tests.infrastructure.database import init_test_db, get_test_session, test_db
from game_share_bot.infrastructure.models.base import Base
from game_share_bot.domain.enums.subscription.type import SubscriptionType


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
def mock_session():
    """Мок сессии для unit-тестов"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_state():
    """Мок состояния FSM"""
    state = AsyncMock()
    state.clear = AsyncMock()
    state.set_state = AsyncMock()
    state.get_state = AsyncMock()
    state.update_data = AsyncMock()
    return state


@pytest.fixture
def mock_message():
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock(spec=TgUser)
    message.from_user.id = 123
    message.from_user.full_name = "Test User"
    message.from_user.username = "testuser"
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    message.edit_text = AsyncMock()
    return message


@pytest.fixture
def mock_message_with_contact():
    """Мок сообщения с контактом"""
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock(spec=TgUser)
    message.from_user.id = 123
    message.from_user.full_name = "Test User"
    message.from_user.username = "testuser"
    message.contact = AsyncMock(spec=Contact)
    message.contact.phone_number = "+1234567890"
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    return message


@pytest.fixture
def mock_callback_query():
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = AsyncMock(spec=TgUser)
    callback.from_user.id = 123
    callback.from_user.full_name = "Test User"
    callback.from_user.username = "testuser"
    callback.message = AsyncMock(spec=Message)
    callback.message.edit_text = AsyncMock()
    callback.message.edit_caption = AsyncMock()
    callback.answer = AsyncMock()
    return callback


@pytest.fixture
def mock_user():
    """Создает мок пользователя приложения"""
    from game_share_bot.infrastructure.models import User
    user = User(
        id=1,
        tg_id=123,
        phone="+79991234567",
        name="Test User"
    )
    return user


@pytest.fixture
def mock_subscription_plan():
    """Создает мок плана подписки"""
    from game_share_bot.infrastructure.models import SubscriptionPlan
    plan = SubscriptionPlan(
        id=uuid4(),
        name=SubscriptionType.PREMIUM,
        max_simultaneous_rental=5,
        monthly_price=999.99,
        description="Premium subscription with 5 simultaneous rentals"
    )
    return plan


@pytest.fixture
def mock_subscription(mock_user, mock_subscription_plan):
    """Создает мок активной подписки"""
    from game_share_bot.infrastructure.models import Subscription
    subscription = Subscription(
        id=uuid4(),
        user_id=mock_user.id,
        plan_id=mock_subscription_plan.id,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        is_auto_renewal=True
    )
    subscription.user = mock_user
    subscription.plan = mock_subscription_plan
    return subscription


@pytest.fixture
async def test_subscription_plan(test_session):
    """Создание тестового плана подписки в БД"""
    from game_share_bot.infrastructure.models import SubscriptionPlan

    plan = SubscriptionPlan(
        id=uuid4(),
        name=SubscriptionType.STANDARD,
        max_simultaneous_rental=3,
        monthly_price=499.99,
        description="Standard subscription plan"
    )
    test_session.add(plan)
    await test_session.commit()
    return plan


@pytest.fixture
async def test_subscription(test_session, test_user, test_subscription_plan):
    """Создание тестовой подписки в БД"""
    from game_share_bot.infrastructure.models import Subscription

    subscription = Subscription(
        id=uuid4(),
        user_id=test_user.id,
        plan_id=test_subscription_plan.id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        is_auto_renewal=True
    )
    test_session.add(subscription)
    await test_session.commit()
    return subscription


# Фикстуры для тестовых данных в БД
@pytest.fixture
async def test_user(test_session):
    """Создание тестового пользователя в БД"""
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
    """Создание тестовой игры в БД"""
    from game_share_bot.infrastructure.repositories.game import GameRepository

    repo = GameRepository(test_session)
    game = await repo.create(
        title="Test Game",
        description="Test Description",
        cover_image_url="test_image.jpg"
    )
    return game


@pytest.fixture
def rental_callback_data():
    """Фикстура для создания callback данных аренды"""

    def _create(action="return", rental_id=1):
        return MagicMock(action=action, rental_id=rental_id)

    return _create


@pytest.fixture
def subscription_callback_data():
    """Фикстура для создания callback данных подписки"""

    def _create(action, month_duration=None, subscription_type=None):
        return MagicMock(action=action, month_duration=month_duration, subscription_type=subscription_type)

    return _create


@pytest.fixture(autouse=True)
async def clean_database(test_session):
    """Автоматическая очистка базы данных перед каждым тестом"""
    for table in reversed(Base.metadata.sorted_tables):
        if table.name not in ['discs_status', 'rental_statuses']:
            await test_session.execute(table.delete())
    await test_session.commit()