from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.infrastructure.models import Game
from .base import BaseRepository


class GameRepository(BaseRepository[Game]):
    """
    Репозиторий для работы с моделью Game.
    """
    model = Game

    def __init__(self, session: AsyncSession):
        super().__init__(session)
