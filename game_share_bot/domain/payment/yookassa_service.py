import asyncio
import os
from logging import getLogger
from typing import Tuple

from dotenv import load_dotenv
from yookassa import Configuration, Payment

from game_share_bot.core.services.sub_upgrade import calculate_additional_payment
from game_share_bot.infrastructure.models import SubscriptionPlan, User

logger = getLogger(__name__)
load_dotenv()


def init_yookassa():
    shop_id = os.getenv('YOOKASSA_SHOP_ID')
    key = os.getenv('YOOKASSA_KEY')
    if shop_id is None or key is None:
        raise Exception("yookassa не инициализирована:")
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
            "return_url": f"https://t.me/{os.getenv("BOT_NAME")}"
        },
        "capture": True,
        "description": f"Подписка {subscription_plan.name} на {duration} мес.",
        # TODO: заполнить receipt, https://yookassa.ru/developers/api#create_payment_receipt
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


async def create_upgrade_payment(
        current_subscription: 'Subscription',
        target_plan: 'SubscriptionPlan',
        user: 'User'
) -> Tuple[str, str]:
    """
    Создает платеж ЮKassa для доплаты при повышении тарифа (upgrade).

    Возвращает: (payment_id, confirmation_url)
    """

    # 1. Рассчитываем сумму доплаты
    # Сумма возвращается в копейках/центах (int), поэтому делим на 100.0 для ЮKassa
    additional_amount = calculate_additional_payment(
        current_subscription=current_subscription,
        target_plan=target_plan
    )

    if additional_amount <= 0:
        raise ValueError("Доплата не требуется или новый план дешевле. Платеж не создается.")


    payment_data = {
        "amount": {
            "value": f"{additional_amount:.2f}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"https://t.me/{os.getenv('BOT_NAME')}"
        },
        "capture": True,
        "description": (
            f"Доплата за повышение тарифа с {current_subscription.plan.name} "
            f"до {target_plan.name} (осталось {current_subscription.end_date.strftime('%d.%m.%Y')})"
        ),
        # TODO: заполнить receipt
        "metadata": {
            "user_id": str(user.id),
            "current_plan_id": current_subscription.plan.id,
            "target_plan_id": target_plan.id,
            "subscription_id": str(current_subscription.id)
        }
    }
    try:
        payment = await asyncio.to_thread(Payment.create, payment_data)
        return payment.id, payment.confirmation.confirmation_url
    except Exception as e:
        logger.error(f"Ошибка при создании платежа на апгрейд: {e}")
        raise RuntimeError("Не удалось создать платеж для повышения тарифа.")

async def get_payment_status(payment_id: str) -> Payment:
    payment = await asyncio.to_thread(Payment.find_one, payment_id)
    return payment.status
