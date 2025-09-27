from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from game_share_bot.models import Base


# TODO
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50))