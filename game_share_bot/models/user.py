from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from game_share_bot.models import Base


# TODO
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    role: Mapped[str] = mapped_column(String(20), default="user")