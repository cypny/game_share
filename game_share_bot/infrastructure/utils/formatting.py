from datetime import datetime

from game_share_bot.infrastructure.models import Game
from game_share_bot.infrastructure.models import Subscription
from game_share_bot.infrastructure.models import SubscriptionPlan


def format_game_short(game: Game) -> str:
    desc_short = (game.description[:100] + "...") if len(game.description) > 100 else game.description

    text = f"🎮 <b>{game.title}</b>\n\n"
    text += f"{desc_short}\n\n"
    text += f"/game_{game.id}"
    return text

def format_game_full(game: Game) -> str:
    return format_game_text_full(game.title, game.description)

def format_game_text_full(title: str, description: str) -> str:
    text = f"🎮 <b>{title}</b>\n\n"
    text += f"{description}\n\n"
    return text

def format_games_list(games: list[Game]) -> str:
    return "\n\n---\n\n".join(format_game_full(game) for game in games)

def format_subscription_info(subscription: Subscription) -> str:
    if subscription is None:
        return "У вас нет подписки"
    status = "🟢 Активна" if subscription.end_date > datetime.now() else "🔴 Истекла"
    auto_renew = "✅ Вкл" if subscription.is_auto_renewal else "❌ Выкл"

    return (
        f"🎫 <b>Информация о подписке</b>\n"
        f"├ 📋 Тип: <i>{subscription.plan.name if subscription.plan else 'Не указан'}</i>\n"
        f"├ 🗓️ Начало: <i>{subscription.start_date.strftime('%d.%m.%Y')}</i>\n"
        f"├ 📅 Окончание: <i>{subscription.end_date.strftime('%d.%m.%Y')}</i>\n"
        f"├ 🔄 Автопродление: <i>{auto_renew}</i>\n"
        f"└ 📊 Статус: <i>{status}</i>"
    )

def format_subscription_plan(subscription_plan: SubscriptionPlan) -> str:
    return (
        f"🎫 <b>{subscription_plan.name}</b>\n"
        f"├ 💰 <i>{subscription_plan.monthly_price}₽/месяц</i>\n"
        f"├ 🎮 <i>До {subscription_plan.max_simultaneous_rental} дисков одновременно</i>\n"
        f"└ 📄 <i>{subscription_plan.description or 'Описание отсутствует'}</i>"
    )

