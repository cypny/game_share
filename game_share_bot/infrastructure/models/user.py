import uuid

from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from ...domain.enums.subscription_status import SubscriptionStatus


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
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")
    queues: Mapped[list["QueueEntry"]] = relationship(
        "QueueEntry",
        back_populates="user"
    )

    @property
    def subscription(self) -> "Subscription | None":
        """Возвращает активную подписку пользователя"""
        for sub in self.subscriptions:
            if sub.status == SubscriptionStatus.ACTIVE:
                return sub
        return None
