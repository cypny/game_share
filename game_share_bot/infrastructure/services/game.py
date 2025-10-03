from game_share_bot.infrastructure.models import Game
from game_share_bot.infrastructure.repositories import GameRepository


class GameService:
    def __init__(self, repo: GameRepository):
        self.repo = repo

    async def search_games(self, query: str) -> list[Game]:
        games = await self.repo.get_all()
        return games

    async def get_game_by_id(self, game_id: int) -> Game | None:
        return await self.repo.get_by_id(game_id)
