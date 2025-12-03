from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from game_share_bot.core.callbacks import AdminCallback, RentalCallback
from game_share_bot.core.keyboards.inline.buttons import admin_button, return_button
from game_share_bot.core.keyboards.inline.common import return_kb
from game_share_bot.domain.enums import AdminAction
from game_share_bot.infrastructure.models import Rental


def return_to_admin_main_panel_kb() -> InlineKeyboardMarkup:
    return return_kb(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL))


def return_to_admin_manage_library_panel_kb() -> InlineKeyboardMarkup:
    return return_kb(AdminCallback(action=AdminAction.MANAGE_LIBRARY))


def rental_actions_confirmation_kb(rentals: list[Rental], action_type: str) -> InlineKeyboardMarkup:
    keyboard_buttons = []

    for rental in rentals:
        button_text = f"✅ Подтвердить возврат {rental.disc.game.title}"
        keyboard_buttons.append(
            [
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=RentalCallback(action=f"confirm_{action_type}", rental_id=rental.id).pack(),
                )
            ]
        )

        button_text = f"❌ Отклонить возврат {rental.disc.game.title}"
        keyboard_buttons.append(
            [
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=RentalCallback(action=f"reject_{action_type}", rental_id=rental.id).pack(),
                )
            ]
        )

    keyboard_buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад в админ-панель",
                callback_data=AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL).pack(),
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def admin_main_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [admin_button("Управление библиотекой", AdminAction.MANAGE_LIBRARY)],
            [admin_button("Выдать админку", AdminAction.APPOINT)],
            [admin_button("Статистика", AdminAction.VIEW_STATS)],
            [
                admin_button("Запросы на возврат", AdminAction.VIEW_RETURN_REQUESTS),
                admin_button("Запросы на получение", AdminAction.VIEW_TAKE_REQUESTS),
            ],
        ]
    )


def admin_manage_library_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                admin_button("Добавить игру", AdminAction.ADD_GAME),
                admin_button("Удалить игру", AdminAction.DELETE_GAME),
            ],
            [
                admin_button("Добавить диск", AdminAction.ADD_DISK),
                admin_button("Удалить диск", AdminAction.DELETE_DISK),
            ],
            [
                return_button(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL)),
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
                return_button(AdminCallback(action=AdminAction.MANAGE_LIBRARY)),
                admin_button("Пропустить", AdminAction.SKIP_IMAGE_INPUT),
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



