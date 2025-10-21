import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from game_share_bot.infrastructure.models.base import Base


class TestDatabase:
    def __init__(self, database_url="sqlite+aiosqlite:///:memory:"):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None

    async def create_engine(self):
        """Создание тестового движка БД"""
        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            future=True
        )
        return self.engine

    async def create_tables(self):
        """Создание всех таблиц"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    async def create_session_factory(self):
        """Создание фабрики сессий"""
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        return self.session_factory

    async def init_database(self):
        """Инициализация всей БД"""
        await self.create_engine()
        await self.create_tables()
        await self.create_session_factory()
        return self

    async def get_session(self):
        """Получение новой сессии"""
        if not self.session_factory:
            await self.init_database()
        return self.session_factory()

    async def dispose(self):
        """Очистка ресурсов"""
        if self.engine:
            await self.engine.dispose()


# Глобальный экземпляр тестовой БД
test_db = TestDatabase()


async def init_test_db():
    """Инициализация тестовой БД для использования в фикстурах"""
    return await test_db.init_database()


async def get_test_session():
    """Получение тестовой сессии"""
    return await test_db.get_session()