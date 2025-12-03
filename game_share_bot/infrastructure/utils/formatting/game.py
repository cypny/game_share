from game_share_bot.infrastructure.models import Game, GameCategory


def format_game_short(game: Game) -> str:
    desc_short = (game.description[:100] + "...") if len(game.description) > 100 else game.description

    text = f"🎮 <b>{game.title}</b>\n\n"
    text += f"{desc_short}\n\n"
    text += f"/game_{game.id}"
    return text


def format_game_full(game: Game, status_info: "GameStatusInfo") -> str:
    categories_text = "🏷️ " + ", ".join(
        [category.name for category in game.categories]) if game.categories else "🏷️ Категории не указаны"

    message_lines = [
        f"🎮 <b>{game.title}</b>",
        f"",
        f"{game.description}",
        f"",
        f"{categories_text}",
        f"",
        f"{status_info.availability_status}",
        f"{status_info.queue_status}",
        f"",
        f"/game_{game.id}"
    ]

    return "\n".join(message_lines)


def format_game_text_full(title: str, description: str, discs_count: int, categories: list[GameCategory]) -> str:
    text = f"🎮 <b>{title}</b>\n\n"
    if categories:
        text += f"🏷️ Категории: {', '.join([category.name for category in categories])}\n"
    else:
        text += "🏷️ Категории не указаны\n"
    text += f"💿 Кол-во дисков: {discs_count}\n\n"
    text += f"{description}\n\n"
    return text


def format_games_list(games: list[Game]) -> str:
    if not games:
        return "Нет доступных игр."

    result = []

    for game in games:
        game_text = f"🎮 {game.title}  /game_{game.id}"
        result.append(game_text)

    return "\n\n".join(result)
