import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from game_share_bot.infrastructure.models.base import Base


class TestDatabase:
    def __init__(self, database_url="sqlite+aiosqlite:///:memory:"):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None

    async def create_engine(self):
        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            future=True
        )
        return self.engine

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    async def create_session_factory(self):
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        return self.session_factory

    async def init_database(self):
        await self.create_engine()
        await self.create_tables()
        await self.create_session_factory()
        return self

    async def get_session(self):
        if not self.session_factory:
            await self.init_database()
        return self.session_factory()

    async def dispose(self):
        if self.engine:
            await self.engine.dispose()


test_db = TestDatabase()


async def init_test_db():
    return await test_db.init_database()


async def get_test_session():
    return await test_db.get_session()