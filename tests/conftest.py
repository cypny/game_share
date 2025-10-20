import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import User, Message, Contact, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_user():
    return User(
        id=123,
        is_bot=False,
        first_name="Test",
        username="test_user"
    )

@pytest.fixture
def mock_message(mock_user):
    msg = MagicMock(spec=Message)
    msg.from_user = mock_user
    msg.answer = AsyncMock()
    msg.reply_markup = None
    return msg

@pytest.fixture
def mock_message_with_contact(mock_user):
    msg = MagicMock(spec=Message)
    msg.from_user = mock_user
    msg.contact = MagicMock(spec=Contact)
    msg.contact.phone_number = "1234567890"
    msg.contact.first_name = "Test"
    msg.contact.user_id = 123
    msg.answer = AsyncMock()
    return msg

@pytest.fixture
def mock_callback_query(mock_user):
    cb = MagicMock(spec=CallbackQuery)
    cb.from_user = mock_user
    cb.message = MagicMock()
    cb.message.answer = AsyncMock()
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    return cb

@pytest.fixture
def mock_state():
    state = MagicMock(spec=FSMContext)
    state.clear = AsyncMock()
    state.set_state = AsyncMock()
    return state

@pytest.fixture
def mock_session():
    session = MagicMock(spec=AsyncSession)
    return session