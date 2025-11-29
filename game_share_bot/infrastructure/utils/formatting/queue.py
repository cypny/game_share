from datetime import timedelta

from game_share_bot.infrastructure.models import Rental
from game_share_bot.infrastructure.repositories.rental.queue_entry import QueueFullInfo


def format_my_queue(queues_info: list[QueueFullInfo], rentals_to_take: list[Rental]) -> str:
    text_lines = []

    # Блок аренд, ожидающих получение
    if rentals_to_take:
        text_lines.append("🎯 <b>Аренды, готовые к получению:</b>")
        for rental in rentals_to_take:
            rental_line = (
                f"🎮 <b>{rental.disc.game.title}</b>\n"
                # TODO: вынести это
                f"⏰ Взять до: {(rental.created_at + timedelta(weeks=1)).strftime('%d.%m.%Y %H:%M')}\n"
            )
            text_lines.append(rental_line)
        text_lines.append("")

    # Блок очередей
    if queues_info:
        text_lines.append("📋 <b>Мои очереди:</b>")
        for info in queues_info:
            queue_line = (
                f"🎮 <b>{info.game.title}</b>\n"
                f"📅 В очереди с {info.queue_entry.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"🏁 Позиция: <b>{info.position}/{info.total_in_queue}</b>\n"
            )
            text_lines.append(queue_line)
    else:
        text_lines.append(
            "📭 <b>Вы не состоите ни в одной очереди</b>\n\n"
            "Добавьте игры в очередь, чтобы арендовать их, когда они станут доступны."
        )

    return "\n".join(text_lines)
