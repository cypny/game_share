import uuid
from datetime import datetime

from sqlalchemy import DateTime, Boolean, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from game_share_bot.infrastructure.models.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
                                               nullable=False, unique=True,)
    plan_id: Mapped[int] = mapped_column(Integer,
                                               ForeignKey("subscription_plans.id", ondelete="CASCADE"), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_auto_renewal: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="subscription")
    plan: Mapped["SubscriptionPlan"] = relationship(back_populates="subscriptions")
