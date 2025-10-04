from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession


# TODO
def init_db(conn_string_async: str) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(conn_string_async, echo=True)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return engine, session_maker
