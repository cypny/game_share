from enum import IntEnum


class RentalStatusEnum(IntEnum):
    """Статусы аренды игровых дисков"""
    ACTIVE = 1
    COMPLETED = 2
    OVERDUE = 3
    PENDING_RETURN = 4