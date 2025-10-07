from game_share_bot.infrastructure.models import Game

def format_game_short(game: Game) -> str:
    text = f"1. <b>{game.title}</b>\n\n"
    return text

def format_game_full(game: Game) -> str:
    text = f"🎮 <b>{game.title}</b>\n\n"
    text += f"{game.description}\n\n"
    return text

def format_games_list(games: list[Game]) -> str:
    return "\n\n---\n\n".join(format_game_full(game) for game in games)

