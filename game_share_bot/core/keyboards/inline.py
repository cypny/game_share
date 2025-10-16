from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from game_share_bot.core.callbacks import CatalogCallback, AdminCallback, MenuCallback
from game_share_bot.core.callbacks.confirmation import ConfirmationCallback
from game_share_bot.core.callbacks.subscription import SubscriptionCallback
from game_share_bot.core.keyboards.buttons import _return_button, return_kb
from game_share_bot.domain.enums import AdminAction
from game_share_bot.domain.enums.subscription.action import SubscriptionAction
from game_share_bot.infrastructure.models import Rental


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Каталог", callback_data=CatalogCallback().pack())],
            [InlineKeyboardButton(text="👤 Личный кабинет", callback_data=MenuCallback(section='personal').pack())],
            [InlineKeyboardButton(text="🆘 Поддержка", callback_data="help")],
        ]
    )


def personal_cabinet_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Арендованные диски",
                                  callback_data=MenuCallback(section='rented_disks').pack())],
            [InlineKeyboardButton(text="📦 Управление подпиской",
                                  callback_data=SubscriptionCallback(action=SubscriptionAction.INFO).pack())],
            [InlineKeyboardButton(text="📋 Моя очередь", callback_data=MenuCallback(section='my_queue').pack())],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=MenuCallback(section='main').pack())]
        ]
    )


def rentals_kb(rentals: list[Rental]) -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками возврата для каждого диска"""
    keyboard_buttons = []

    for rental in rentals:
        # Показываем кнопку возврата только для активных аренд
        if rental.status_id == RentalStatusEnum.ACTIVE:
            button_text = f"🔙 Вернуть {rental.disc.game.title}"
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=RentalCallback(action="return", rental_id=rental.id).pack()
                )
            ])

    keyboard_buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=MenuCallback(section='personal').pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавить игру",
                                     callback_data=AdminCallback(action=AdminAction.ADD_GAME).pack()),
                InlineKeyboardButton(text="Удалить игру",
                                     callback_data=AdminCallback(action=AdminAction.DELETE_GAME).pack())
            ],
            [
                InlineKeyboardButton(text="Выдать админку",
                                     callback_data=AdminCallback(action=AdminAction.APPOINT).pack())
            ],
            [
                InlineKeyboardButton(text="📋 Запросы на возврат",
                                     callback_data=AdminCallback(action=AdminAction.VIEW_RETURN_REQUESTS).pack())
            ]
        ]
    )


def confirmation_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=ConfirmationCallback(is_confirmed=True).pack())],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=ConfirmationCallback(is_confirmed=False).pack())]
        ]
    )


def add_game_image_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _return_button(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL)),
                InlineKeyboardButton(text="Пропустить",
                                     callback_data=AdminCallback(action=AdminAction.SKIP_IMAGE_INPUT).pack())
            ]
        ]
    )


def return_to_admin_panel_kb() -> InlineKeyboardMarkup:
    return return_kb(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL))
