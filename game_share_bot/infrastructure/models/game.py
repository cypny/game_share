from sqlalchemy import String, Text, Integer, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

game_category_association = Table(
    'game_category_mapping',
    Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('game_categories.id'), primary_key=True)
)

class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    cover_image_url: Mapped[str] = mapped_column(Text, nullable=True)

    discs: Mapped[list["Disc"]] = relationship(back_populates="game")
    categories: Mapped[list["GameCategory"]] = relationship(
        "GameCategory",
        secondary=game_category_association,
        back_populates="games"
    )
    queues: Mapped[list["QueueEntry"]] = relationship(
        "QueueEntry",
        back_populates="game"
    )

class GameCategory(Base):
    __tablename__ = "game_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    games: Mapped[list["Game"]] = relationship(
        "Game",
        secondary=game_category_association,
        back_populates="categories"
    )
