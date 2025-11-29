from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from game_share_bot.core.callbacks import AdminCallback, RentalCallback
from game_share_bot.core.keyboards.inline.common import return_kb
from game_share_bot.core.keyboards.inline.buttons import return_button
from game_share_bot.infrastructure.models import Rental
from game_share_bot.domain.enums import AdminAction


def return_to_admin_panel_kb() -> InlineKeyboardMarkup:
    return return_kb(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL))


def rental_actions_confirmation_kb(rentals: list[Rental], action_type: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками подтверждения/отклонения возвратов"""
    keyboard_buttons = []

    for rental in rentals:
        button_text = f"✅ Подтвердить возврат {rental.disc.game.title}"
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=RentalCallback(action=f"confirm_{action_type}", rental_id=rental.id).pack()
            )
        ])

        button_text = f"❌ Отклонить возврат {rental.disc.game.title}"
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=RentalCallback(action=f"reject_{action_type}", rental_id=rental.id).pack()
            )
        ])

    keyboard_buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад в админ-панель",
            callback_data=AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL).pack()
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
            ],
            [
                InlineKeyboardButton(text="Создать рассылку",
                                     callback_data=AdminCallback(action=AdminAction.CREATE_NOTIFICATION).pack())
            ]
        ]
    )

def add_game_image_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                return_button(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL)),
                InlineKeyboardButton(text="Пропустить",
                                     callback_data=AdminCallback(action=AdminAction.SKIP_IMAGE_INPUT).pack())
            ]
        ]
    )

def send_notification_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Все пользователи",
                    callback_data=AdminCallback(action=AdminAction.SEND_NOTIFICATION_TO_ALL).pack()),
                InlineKeyboardButton(
                    text="Пользователи с подпиской",
                    callback_data=AdminCallback(action=AdminAction.SEND_NOTIFICATION_TO_ACTIVE).pack()),
            ],
            [
                return_button(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL))
            ]
        ]
    )



