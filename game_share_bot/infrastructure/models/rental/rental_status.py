from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from game_share_bot.infrastructure.models.base import Base


class RentalStatus(Base):
    __tablename__ = "rental_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String)
