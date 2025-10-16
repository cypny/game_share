from .catalog import CatalogCallback
from .game import GameCallback
from .menu import MenuCallback
from .user import UserCallback
from .admin import AdminCallback
from .confirmation import ConfirmationCallback
from .rental import RentalCallback

__all__ = [
    "MenuCallback",
    "CatalogCallback",
    "GameCallback",
    "UserCallback",
    "AdminCallback",
    "ConfirmationCallback",
    "RentalCallback"
]