from enum import IntEnum


class RentalStatus(IntEnum):
    """Статусы аренды игровых дисков"""
    ACTIVE = 1
    COMPLETED = 2
    OVERDUE = 3
    PENDING_RETURN = 4


class DiscStatus(IntEnum):
    """Статусы игровых дисков"""
    AVAILABLE = 1
    RENTED = 2
    MAINTENANCE = 3
    PENDING_RETURN = 4