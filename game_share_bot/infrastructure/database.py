from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession

from game_share_bot.infrastructure.repositories.debug import DebugRepository

#TODO
async def init_db(conn_string_async: str) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(conn_string_async, echo=True)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    # Добавляем тестовые данные если БД пустая
    async with session_maker() as session:
        debug_repo = DebugRepository(session)
        await debug_repo.populate_test_games()

    return engine, session_maker