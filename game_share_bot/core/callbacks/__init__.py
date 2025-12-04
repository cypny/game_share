from .admin import AdminCallback
from .games.catalog import CatalogCallback
from .confirmation import ConfirmationCallback, TakeDiscConfirmationCallback
from .games.game import GameCallback
from .menu import MenuCallback
from .rental.rental import RentalCallback
from .subscription import SubscriptionCallback
from .user import UserCallback

__all__ = [
    "MenuCallback",
    "CatalogCallback",
    "GameCallback",
    "UserCallback",
    "AdminCallback",
    "ConfirmationCallback",
    "TakeDiscConfirmationCallback",
    "RentalCallback",
    "SubscriptionCallback"
]
