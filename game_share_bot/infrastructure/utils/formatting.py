from models import Game

def format_game_short(game: Game) -> str:
    desc_short = (game.description[:100] + "...") if len(game.description) > 100 else game.description

    text = f"🎮 <b>{game.title}</b>\n\n"
    text += f"{desc_short}\n\n"
    text += f"/game_{game.id}"
    return text

def format_game_full(game: Game) -> str:
    text = f"🎮 <b>{game.title}</b>\n\n"
    text += f"{game.description}\n\n"
    return text

def format_games_list(games: list[Game]) -> str:
    return "\n\n---\n\n".join(format_game_full(game) for game in games)

