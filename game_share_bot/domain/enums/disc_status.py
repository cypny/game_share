from enum import IntEnum

#TODO: еще статус PENDING_TAKE тут и у rental. Подумать
class DiscStatus(IntEnum):
    """Статусы игровых дисков"""
    AVAILABLE = 1
    RENTED = 2
    MAINTENANCE = 3
    PENDING_RETURN = 4