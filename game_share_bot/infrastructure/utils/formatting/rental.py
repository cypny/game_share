from game_share_bot.domain.enums import RentalStatus
from game_share_bot.infrastructure.models import Rental


def format_rental_full(rental: Rental) -> str:
    # Форматируем каждую дату с проверкой на None
    if rental.start_date:
        start_date_text = f"📅 <b>Начало аренды:</b> {rental.start_date.strftime('%d.%m.%Y в %H:%M')}"
    else:
        start_date_text = "📅 <b>Начало аренды:</b> <i>не указано</i>"

    if rental.expected_end_date:
        expected_end_text = f"⏰ <b>Вернуть до:</b> {rental.expected_end_date.strftime('%d.%m.%Y в %H:%M')}"
    else:
        expected_end_text = "⏰ <b>Вернуть до:</b> <i>не указано</i>"

    if rental.actual_end_date:
        actual_end_text = f"✅ <b>Фактически вернул:</b> {rental.actual_end_date.strftime('%d.%m.%Y в %H:%M')}"
    else:
        actual_end_text = "✅ <b>Фактически вернул:</b> <i>аренда активна</i>"

    # Собираем всё в красивый список
    lines = [
        f"🎮 <b>Игра:</b> {rental.disc.game.title}",
        f"🆔 <b>Номер аренды:</b> {rental.id}",
        f"💿 <b>ID диска:</b> {rental.disc.disc_id}",
        "",  # Пустая строка для разделения
        start_date_text,
        expected_end_text,
        actual_end_text,
        "",
        f"📊 <b>Статус:</b> {RentalStatus(rental.status_id).name.replace('_', ' ').title()}"
    ]

    return "\n".join(lines)

def format_rental_short(rental: Rental) -> str:
    # Форматируем каждую дату с проверкой на None
    if rental.start_date:
        start_date_text = f"📅 <b>Начало аренды:</b> {rental.start_date.strftime('%d.%m.%Y в %H:%M')}"
    else:
        start_date_text = "📅 <b>Начало аренды:</b> <i>не указано</i>"

    if rental.expected_end_date:
        expected_end_text = f"⏰ <b>Вернуть до:</b> {rental.expected_end_date.strftime('%d.%m.%Y в %H:%M')}"
    else:
        expected_end_text = "⏰ <b>Вернуть до:</b> <i>не указано</i>"

    if rental.actual_end_date:
        actual_end_text = f"✅ <b>Фактически вернул:</b> {rental.actual_end_date.strftime('%d.%m.%Y в %H:%M')}"
    else:
        actual_end_text = "✅ <b>Фактически вернул:</b> <i>аренда активна</i>"

    # Собираем всё в красивый список
    lines = [
        f"👤 @{rental.user.name}",
        f"🎮 <b>Игра:</b> {rental.disc.game.title}",
        start_date_text,
        expected_end_text,
        ""
    ]

    return "\n".join(lines)

def format_pending_take_message(rentals: list[Rental]):
    if not rentals:
        return "Запросы на получения отсутствуют"
    returns_str = "\n\n".join(
        format_rental_short(rental) for rental in rentals
    )
    return f"📋 Запросы на получение ({len(rentals)}):\n\n{returns_str}"

