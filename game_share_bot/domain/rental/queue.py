import uuid
from typing import List, Optional


def get_entry_position(game_id: int, user_id: uuid.UUID, queue_entries: List["QueueEntry"]) -> Optional[int]:
    """Возвращает None, если юзер не в очереди, иначе позицию в очереди (номер 1 получит диск первым)"""
    for pos, entry in enumerate(queue_entries):
        if entry.user_id == user_id:
            return pos + 1
    return None