import uuid
from typing import List, Optional


def get_entry_position(user_id: uuid.UUID, queue_entries: List["QueueEntry"]) -> Optional[int]:
    active_entries = [entry for entry in queue_entries if entry.is_active]
    active_entries.sort(key=lambda e: e.created_at)
    """Возвращает None, если юзер не в очереди, иначе позицию в очереди (номер 1 получит диск первым)"""
    for pos, entry in enumerate(active_entries):
        if entry.user_id == user_id:
            return pos + 1
    return None