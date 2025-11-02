from datetime import datetime, timezone


# from infrastructure.models import SubscriptionPlan, Subscription


def format_subscription_info(subscription: "Subscription") -> str:
    if subscription is None:
        return "У вас нет подписки"
    status = "🟢 Активна" if subscription.end_date > datetime.now(timezone.utc) else "🔴 Истекла"
    auto_renew = "✅ Вкл" if subscription.is_auto_renewal else "❌ Выкл"

    return (
        f"🎫 <b>Информация о подписке</b>\n"
        f"├ 📋 Тип: <i>{subscription.plan.name if subscription.plan else 'Не указан'}</i>\n"
        f"├ 🗓️ Начало: <i>{subscription.start_date.strftime('%d.%m.%Y')}</i>\n"
        f"├ 📅 Окончание: <i>{subscription.end_date.strftime('%d.%m.%Y')}</i>\n"
        f"├ 🔄 Автопродление: <i>{auto_renew}</i>\n"
        f"└ 📊 Статус: <i>{status}</i>"
    )

def format_subscription_plan(subscription_plan: "SubscriptionPlan") -> str:
    return (
        f"🎫 <b>{subscription_plan.name}</b>\n"
        f"├ 💰 <i>{subscription_plan.monthly_price}₽/месяц</i>\n"
        f"├ 🎮 <i>До {subscription_plan.max_simultaneous_rental} дисков одновременно</i>\n"
        f"└ 📄 <i>{subscription_plan.description or 'Описание отсутствует'}</i>"
    )