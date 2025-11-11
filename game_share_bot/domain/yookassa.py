import asyncio
import os
import uuid
from logging import getLogger
from typing import Dict, Any, Tuple

from dotenv import load_dotenv
from yookassa import Configuration, Payment
from yookassa.domain.exceptions import BadRequestError

from game_share_bot.infrastructure.models import SubscriptionPlan, User

logger = getLogger(__name__)

def init_yookassa():
    load_dotenv()
    shop_id = os.getenv('YOOKASSA_SHOP_ID')
    key = os.getenv('YOOKASSA_KEY')
    if shop_id is None or key is None:
        raise Exception("yookassa не инициализирована")
    Configuration.configure(account_id=shop_id, secret_key=key)


async def create_payment(
        subscription_plan: SubscriptionPlan,
        duration: int,
        user: User
) -> Tuple[str, str]:
    amount = subscription_plan.monthly_price * duration

    payment_data = {
        "amount": {
            "value": f"{amount:.2f}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://merchant-site.ru/return_url"
        },
        "capture": True,
        "description": f"Подписка {subscription_plan.name} на {duration} мес.",
        #TODO: заполнить receipt, https://yookassa.ru/developers/api#create_payment_receipt
        "metadata": {
            "user_id": str(user.id),
            "plan_id": subscription_plan.id,
            "duration": duration
        }
    }

    try:
        payment = await asyncio.to_thread(Payment.create, payment_data)
        return payment.id, payment.confirmation.confirmation_url
    except Exception as e:
        logger.error(f"Ошибка при создании платежа: {e}")
        raise

async def get_payment_status(payment_id: str) -> Payment:
    payment = await asyncio.to_thread(Payment.find_one, payment_id)
    return payment.status
