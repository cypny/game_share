import uuid
from typing import Optional

from sqlalchemy import BigInteger, Numeric, Text, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, validates

from game_share_bot.infrastructure.models.base import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(20), nullable=False)
    max_simultaneous_rental: Mapped[int] = mapped_column(BigInteger, nullable=False)
    monthly_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    @validates("name")
    def validate_name(self, key: str, name: str) -> str:
        if not isinstance(name, str):
            raise ValueError("Subscription plan name must be a string")
        normalized = name.strip().lower().replace(" ", "")
        if not normalized:
            raise ValueError("Subscription plan name cannot be empty after normalization")
        if len(normalized) > 20:
            raise ValueError("Subscription plan name too long after normalization (max 20 chars)")
        return normalized