from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from game_share_bot.models import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    cover_image_url: Mapped[str] = mapped_column(Text, nullable=True)
