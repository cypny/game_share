from game_share_bot.infrastructure.repositories.rental.queue_entry import QueueFullInfo


def format_my_queue(queues_info: list[QueueFullInfo]) -> str:
    if not queues_info:
        return (
            "📭 <b>Вы не состоите ни в одной очереди</b>\n\n"
            "Добавьте игры в очередь, чтобы арендовать их, когда они станут доступны."
        )
    else:
        text_lines = []
        for info in queues_info:
            if info.position == 1:
                # Позиция 1 - можно забирать
                queue_line = (
                    f"🎮 <b>{info.game.title}</b>\n"
                    f"📅 В очереди с {info.queue_entry.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                    f"✅ <b>Позиция 1 - можно забирать!</b>\n"
                    f"🏁 Всего в очереди: {info.total_in_queue}\n"
                )
            else:
                # Обычная позиция
                queue_line = (
                    f"🎮 <b>{info.game.title}</b>\n"
                    f"📅 В очереди с {info.queue_entry.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                    f"🏁 Позиция: <b>{info.position}/{info.total_in_queue}</b>\n"
                )
            text_lines.append(queue_line)

        return "<b>📋 Мои очереди:</b>\n\n" + "\n".join(text_lines)