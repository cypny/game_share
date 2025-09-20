import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

#TODO
load_dotenv()
CONN_STRING = os.getenv("CONN_STRING_ASYNC")


class Base(DeclarativeBase):
    pass


engine = create_async_engine(CONN_STRING, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
