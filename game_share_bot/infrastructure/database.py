import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

#TODO
load_dotenv()
CONN_STRING = os.getenv("CONN_STRING_ASYNC")

engine = create_async_engine(CONN_STRING, echo=True)
session_maker = async_sessionmaker(engine, expire_on_commit=False)
