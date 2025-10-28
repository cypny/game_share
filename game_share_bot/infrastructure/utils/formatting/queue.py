from game_share_bot.infrastructure.repositories.rental.queue_entry import QueueFullInfo


def format_my_queue(queues_info: QueueFullInfo) -> str:
    if not queues_info:
        return (
            "📭 <b>Вы не состоите ни в одной очереди</b>\n\n"
            "Добавьте игры в очередь, чтобы арендовать их, когда они станут доступны."
        )
    else:
        text_lines = []
        for info in queues_info:
            text_lines.append(
                f"🎮 <b>{info.game.title}</b>\n"
                f"📅 В очереди с {info.queue_entry.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"🏁 Позиция: <b>{info.position}/{info.total_in_queue}</b>\n"
                f"⏱️ Примерное время: ~{info.position * 7} дней\n"
            )

        return "<b>📋 Мои очереди:</b>\n\n" + "\n".join(text_lines)