from enum import IntEnum


class SubscriptionStatus(IntEnum):
    """Статусы аренды игровых дисков"""
    PENDING_PAYMENT = 1
    CANCELED = 2
    ACTIVE = 3
    ENDED = 4