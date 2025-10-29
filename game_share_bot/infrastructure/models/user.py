import uuid

from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    role: Mapped[str] = mapped_column(String(20), default="user")

    rentals: Mapped[list["Rental"]] = relationship(back_populates="user")
    subscription: Mapped["Subscription"] = relationship(back_populates="user")
