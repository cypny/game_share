from enum import IntEnum


class DiscStatusEnum(IntEnum):
    """Статусы игровых дисков"""
    AVAILABLE = 1
    RENTED = 2
    MAINTENANCE = 3
    PENDING_RETURN = 4