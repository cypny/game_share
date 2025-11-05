from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from game_share_bot.core.callbacks import CatalogCallback, MenuCallback, RentalCallback, SubscriptionCallback
from game_share_bot.core.keyboards.inline.buttons import return_button
from game_share_bot.domain.enums import MenuSection, RentalStatus, SubscriptionAction
from game_share_bot.infrastructure.models import Rental


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Каталог", callback_data=CatalogCallback().pack())],
            [InlineKeyboardButton(text="👤 Личный кабинет",
                                  callback_data=MenuCallback(section=MenuSection.PERSONAL_CABINET).pack())],
            [InlineKeyboardButton(text="🆘 Поддержка", callback_data="help")],
        ]
    )


def personal_cabinet_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Арендованные диски",
                                  callback_data=MenuCallback(section=MenuSection.RENTED_DISKS).pack())],
            [InlineKeyboardButton(text="📦 Управление подпиской",
                                  callback_data=SubscriptionCallback(action=SubscriptionAction.INFO).pack())],
            [InlineKeyboardButton(text="📋 Моя очередь",
                                  callback_data=MenuCallback(section=MenuSection.QUEUE).pack())],
            [InlineKeyboardButton(text="⬅️ Назад",
                                  callback_data=MenuCallback(section=MenuSection.MAIN).pack())]
        ]
    )


def rentals_kb(rentals: list[Rental]) -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками возврата для каждого диска"""
    keyboard_buttons = []

    for rental in rentals:
        # Показываем кнопку возврата только для активных аренд
        if rental.status_id == RentalStatus.ACTIVE:
            button_text = f"🔙 Вернуть {rental.disc.game.title}"
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=RentalCallback(action="return", rental_id=rental.id).pack()
                )
            ])

    keyboard_buttons.append([
        return_button(MenuCallback(section=MenuSection.PERSONAL_CABINET))
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def catalog_keyboard(current_page: int, total_games: int, page_size: int, query: str) -> InlineKeyboardMarkup:
    """Клавиатура для каталога с пагинацией"""
    total_pages = (total_games + page_size - 1) // page_size
    buttons = []

    # Кнопки пагинации
    pagination_buttons = []

    if current_page > 0:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=CatalogCallback(query=query, page=current_page - 1).pack()
            )
        )

    # Информация о странице
    pagination_buttons.append(
        InlineKeyboardButton(
            text=f"{current_page + 1}/{total_pages}",
            callback_data="no_action"
        )
    )

    if current_page < total_pages - 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=CatalogCallback(query=query, page=current_page + 1).pack()
            )
        )

    if pagination_buttons:
        buttons.append(pagination_buttons)

    # Кнопка возврата
    buttons.append([
        InlineKeyboardButton(
            text="◀️ В главное меню",
            callback_data=MenuCallback(section=MenuSection.MAIN).pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
