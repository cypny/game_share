import uuid

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from game_share_bot.infrastructure.models.base import Base


class Disc(Base):
    __tablename__ = "general_discs"

    disc_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    game_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("games.id"))
    status_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("discs_status.id"))

    game: Mapped["Game"] = relationship(back_populates="discs")
    status: Mapped["DiscStatus"] = relationship()
