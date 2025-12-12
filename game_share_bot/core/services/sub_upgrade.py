import math
from datetime import datetime, timezone

from game_share_bot.infrastructure.models import Subscription, SubscriptionPlan


def calculate_additional_payment(
        current_subscription: Subscription,
        target_plan: SubscriptionPlan
) -> int:
    """
    Рассчитывает доплату при переходе на более дорогой тариф.

    Алгоритм:
    1. Считаем разницу в цене за месяц между новым и старым планом.
    2. Считаем оставшееся время подписки.
    3. Конвертируем оставшееся время в месяцы (1 день считается как целый месяц).
    4. Умножаем разницу цены на количество оставшихся "месяцев".
    """

    current_plan = current_subscription.plan
    price_diff = target_plan.monthly_price - current_plan.monthly_price

    if price_diff <= 0:
        return 0

    now = datetime.now(timezone.utc)
    end_date = current_subscription.end_date
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)

    days_remaining = (end_date - now).days

    if days_remaining <= 0:
        return 0

    months_remaining = math.ceil(days_remaining / 30)

    return math.ceil(price_diff * months_remaining)