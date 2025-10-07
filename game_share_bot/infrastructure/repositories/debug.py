from sqlalchemy.ext.asyncio import AsyncSession
from game_share_bot.infrastructure.models.game import Game


class DebugRepository:
    """
    Репозиторий для дебага и тестовых данных.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_database_empty(self) -> bool:
        """
        Проверяет, пустая ли БД (нет игр).
        """
        from sqlalchemy import select
        result = await self.session.execute(select(Game).limit(1))
        return result.scalar_one_or_none() is None

    async def populate_test_games(self) -> None:
        """
        Добавляет тестовые игры если БД пустая.
        Если не пустая - забивает хуй.
        """
        if not await self.is_database_empty():
            return  # БД не пустая - забиваем хуй

        test_games = [
            Game(
                title="The Witcher 3: Wild Hunt",
                description="Action RPG в мире фэнтези",
                cover_image_url="https://image.winudf.com/v2/image/bW9iaS5hbmRyb2FwcC5wcm9zcGVyaXR5YXBwcy5jNTExMV9zY3JlZW5fN18xNTI0MDQxMDUwXzAyMQ/screen-7.jpg?fakeurl=1&type=.jpg"
            ),
            Game(
                title="Cyberpunk 2077",
                description="Научно-фантастический экшен RPG",
                cover_image_url="https://image.winudf.com/v2/image/bW9iaS5hbmRyb2FwcC5wcm9zcGVyaXR5YXBwcy5jNTExMV9zY3JlZW5fN18xNTI0MDQxMDUwXzAyMQ/screen-7.jpg?fakeurl=1&type=.jpg"
            ),
            Game(
                title="Red Dead Redemption 2",
                description="Приклюденческий вестерн-экшен",
                cover_image_url="https://image.winudf.com/v2/image/bW9iaS5hbmRyb2FwcC5wcm9zcGVyaXR5YXBwcy5jNTExMV9zY3JlZW5fN18xNTI0MDQxMDUwXzAyMQ/screen-7.jpg?fakeurl=1&type=.jpg"
            ),
            Game(
                title="The Legend of Zelda: Breath of the Wild",
                description="Приключенческая игра с открытым миром",
                cover_image_url="https://image.winudf.com/v2/image/bW9iaS5hbmRyb2FwcC5wcm9zcGVyaXR5YXBwcy5jNTExMV9zY3JlZW5fN18xNTI0MDQxMDUwXzAyMQ/screen-7.jpg?fakeurl=1&type=.jpg"
            ),
            Game(
                title="God of War",
                description="Экшен-адвенчура в скандинавской мифологии",
                cover_image_url="https://image.winudf.com/v2/image/bW9iaS5hbmRyb2FwcC5wcm9zcGVyaXR5YXBwcy5jNTExMV9zY3JlZW5fN18xNTI0MDQxMDUwXzAyMQ/screen-7.jpg?fakeurl=1&type=.jpg"
            )
        ]

        self.session.add_all(test_games)
        await self.session.commit()