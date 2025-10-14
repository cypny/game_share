from datetime import datetime

from game_share_bot.infrastructure.models import Game
from game_share_bot.infrastructure.models import Subscription


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

def format_subscription(subscription: Subscription) -> str:
    if subscription is None:
        return "У вас нет подписки"
    return (
        f"📋 **Информация о подписке**\n"
        f"├ Тип: {subscription.plan.name if subscription.plan else 'N/A'}\n"
        f"├ Начало: {subscription.start_date.strftime('%d.%m.%Y')}\n"
        f"├ Окончание: {subscription.end_date.strftime('%d.%m.%Y')}\n"
        f"├ Автопродление: {'✅' if subscription.is_auto_renewal else '❌'}\n"
        f"└ Статус: {'🔴 Активна' if subscription.end_date > datetime.now() else '⚪ Истекла'}"
    )

