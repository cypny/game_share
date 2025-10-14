from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from game_share_bot.infrastructure.models.base import Base


class DiscStatus(Base):
    __tablename__ = "discs_status"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String)
