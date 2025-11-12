from typing import Optional

from game_share_bot.infrastructure.models import Game
from game_share_bot.domain.enums.disc_status import DiscStatus


def format_game_short(game: Game) -> str:
    desc_short = (game.description[:100] + "...") if len(game.description) > 100 else game.description

    text = f"🎮 <b>{game.title}</b>\n\n"
    text += f"{desc_short}\n\n"
    text += f"/game_{game.id}"
    return text


def format_game_full(
        game: Game,
        available_discs_count: int,
        user_queue_position: int | None,
        availability_text
) -> str:
    if user_queue_position is not None:
        queue_status_text = f"Ваша позиция в очереди: {user_queue_position}"
    else:
        queue_status_text = availability_text

    if available_discs_count > 0:
        availability_text = f"✅ Доступно дисков: {available_discs_count}"
    else:
        availability_text = "❌ Все диски заняты"

    if game.categories:
        categories_text = "🏷️ " + ", ".join([category.name for category in game.categories])
    else:
        categories_text = "🏷️ Категории не указаны"

    return (
        f"🎮 <b>{game.title}</b>\n\n"
        f"{game.description}\n\n"
        f"{categories_text}\n\n"
        f"{availability_text}\n\n"
        f"{queue_status_text}\n\n"
        f"/game_{game.id}"
    )


def format_game_text_full(title: str, description: str) -> str:
    text = f"🎮 <b>{title}</b>\n\n"
    text += f"{description}\n\n"
    return text


def format_games_list(games: list[Game]) -> str:
    if not games:
        return "Нет доступных игр."

    result: list[str] = []

    for game in games:
        discs = getattr(game, "discs", []) or []
        total = len(discs)
        if total == 0:
            continue

        available = sum(1 for d in discs if d.status_id == DiscStatus.AVAILABLE)
        if available <= 0:
            continue


        if game.categories:
            genres = ", ".join(category.name for category in game.categories)
        else:
            genres = "Без жанра"

        block = (
            f"{game.title}  ({available} / {total} дисков)\n"
            f"{genres}\n"
            f"/game_{game.id}"
        )
        result.append(block)

    if not result:
        return "Нет доступных игр."

    return "\n\n".join(result)
