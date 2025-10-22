from game_share_bot.infrastructure.models import Game


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