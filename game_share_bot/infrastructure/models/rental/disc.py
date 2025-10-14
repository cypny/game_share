from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from game_share_bot.infrastructure.models.base import Base


class Disc(Base):
    __tablename__ = "general_discs"

    disc_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    game_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("games.id"))
    status_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("discs_status.id"))

    game: Mapped["Game"] = relationship(back_populates="discs")
    status: Mapped["DiscStatus"] = relationship()
