from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Rental(Base):
    __tablename__ = "rentals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    disc_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("general_discs.disc_id"))
    status_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rental_statuses.id"))
    start_date: Mapped[datetime] = mapped_column(DateTime)
    expected_end_date: Mapped[datetime] = mapped_column(DateTime)
    actual_end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship()
    disc: Mapped["Disc"] = relationship()
    status: Mapped["RentalStatus"] = relationship()
