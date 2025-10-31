from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from game_share_bot.core.callbacks import RentalCallback, MenuCallback
from game_share_bot.core.keyboards import return_button
from game_share_bot.domain.enums import RentalStatus, MenuSection
from game_share_bot.infrastructure.models import Rental


def my_queue_kb(pending_take_rentals: list[Rental]) -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками возврата для каждого диска"""
    keyboard_buttons = []

    for rental in pending_take_rentals:
        # Показываем кнопку возврата только для активных аренд
        if rental.status_id == RentalStatus.PENDING_TAKE:
            button_text = f"🔙 Взять {rental.disc.game.title}"
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=RentalCallback(action="take", rental_id=rental.id).pack()
                )
            ])

    keyboard_buttons.append([
        return_button(MenuCallback(section=MenuSection.PERSONAL_CABINET))
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
