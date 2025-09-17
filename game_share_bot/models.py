from datetime import datetime
from typing import Optional, List


class User:
    def __init__(
        self,
        user_id: int,
        username: Optional[str],
        last_login: datetime,
        role: str = "user"
    ):
        self.user_id = user_id
        self.username = username
        self.last_login = last_login
        self.role = role


class Game:
    def __init__(
        self,
        game_id: int,
        title: str,
        description: str,
        cover_image_url: str,
        rental_price: float,
        rating: float = 0.0,
        is_available: bool = True,
        genres: Optional[List[str]] = None
    ):
        self.game_id = game_id
        self.title = title
        self.description = description
        self.cover_image_url = cover_image_url
        self.rental_price = rental_price
        self.rating = rating
        self.is_available = is_available
        self.genres = genres if genres is not None else []


class Rental:
    def __init__(
        self,
        rental_id: int,
        user_id: int,
        game_id: int,
        purchase_date: datetime,
        start_date: datetime,
        end_date: datetime,
        status: str,
        auto_renewal: bool = False,
        is_active: bool = True
    ):
        self.rental_id = rental_id
        self.user_id = user_id
        self.game_id = game_id
        self.purchase_date = purchase_date
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.auto_renewal = auto_renewal
        self.is_active = is_active


class Transaction:
    def __init__(
        self,
        transaction_id: int,
        user_id: int,
        rental_id: int,
        yookassa_payment_id: str,
        status: str,
        amount: float,
        currency: str = "RUB",
        created_at: Optional[datetime] = None,
        description: Optional[str] = None
    ):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.rental_id = rental_id
        self.yookassa_payment_id = yookassa_payment_id
        self.status = status
        self.amount = amount
        self.currency = currency
        self.created_at = created_at
        self.description = description