from domain.enums import RentalStatus

from typing import TYPE_CHECKING



def format_rented_disks_message(rentals: list["Rental"]) -> str:
    """Форматирует сообщение со списком арендованных дисков"""
    if not rentals:
        return "📦 У вас нет арендованных дисков"

    disks_list = []
    for rental in rentals:
        game_title = rental.disc.game.title
        start_date = rental.start_date.strftime("%d.%m.%Y")
        end_date = rental.expected_end_date.strftime("%d.%m.%Y")

        disk_info = (
            f"🎮 {game_title}\n"
            f"📅 Дата получения: {start_date}\n"
            f"⏰ Сдать до: {end_date}"
        )

        if rental.status_id == RentalStatus.PENDING_RETURN:
            disk_info += "\n⏳ Ожидает подтверждения возврата администратором"

        disks_list.append(disk_info)

    disks_str = "\n\n".join(disks_list)
    return f"📦 Ваши арендованные диски:\n\n{disks_str}"
