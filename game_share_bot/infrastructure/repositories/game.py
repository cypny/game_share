from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Game
from infrastructure.repositories.base import BaseRepository


class GameRepository(BaseRepository[Game]):
    """
    Репозиторий для работы с моделью Game.
    """
    model = Game

    def __init__(self, session: AsyncSession):
        super().__init__(session)
