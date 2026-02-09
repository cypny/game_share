from typing import List, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from game_share_bot.core.callbacks import AdminCallback, RentalCallback
from game_share_bot.core.keyboards.inline.buttons import admin_button, return_button
from game_share_bot.core.keyboards.inline.common import return_kb
from game_share_bot.domain.enums import AdminAction, SubscriptionType
from game_share_bot.infrastructure.models import Rental


def return_to_admin_main_panel_kb() -> InlineKeyboardMarkup:
    return return_kb(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL))


def return_to_admin_manage_library_panel_kb() -> InlineKeyboardMarkup:
    return return_kb(AdminCallback(action=AdminAction.MANAGE_LIBRARY))


def rental_actions_confirmation_kb(rentals: list[Rental], action_type: str) -> InlineKeyboardMarkup:
    keyboard_buttons = []

    # Определяем текст действия в зависимости от типа
    action_text = "возврат" if action_type == "return" else "получение"

    for rental in rentals:
        button_text = f"✅ Подтвердить {action_text} {rental.disc.game.title}"
        keyboard_buttons.append(
            [
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=RentalCallback(action=f"confirm_{action_type}", rental_id=rental.id).pack(),
                )
            ]
        )

        button_text = f"❌ Отклонить {action_text} {rental.disc.game.title}"
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


def rental_action_single_kb(rental: Rental, action_type: str, current_page: int, total_count: int, admin_action: AdminAction) -> InlineKeyboardMarkup:
    """Создает клавиатуру для одного rental с кнопками действия и пагинацией"""
    keyboard_buttons = []

    # Определяем текст действия в зависимости от типа
    action_text = "возврат" if action_type == "return" else "получение"

    # Кнопки действия
    keyboard_buttons.append([
        InlineKeyboardButton(
            text=f"✅ Подтвердить {action_text}",
            callback_data=RentalCallback(action=f"confirm_{action_type}", rental_id=rental.id).pack(),
        )
    ])

    keyboard_buttons.append([
        InlineKeyboardButton(
            text=f"❌ Отклонить {action_text}",
            callback_data=RentalCallback(action=f"reject_{action_type}", rental_id=rental.id).pack(),
        )
    ])

    # Пагинация
    pagination_buttons = []
    if current_page > 0:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Предыдущий",
                callback_data=AdminCallback(action=admin_action, page=current_page - 1).pack()
            )
        )

    if current_page < total_count - 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="Следующий ➡️",
                callback_data=AdminCallback(action=admin_action, page=current_page + 1).pack()
            )
        )

    if pagination_buttons:
        keyboard_buttons.append(pagination_buttons)

    # Кнопка возврата
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад в админ-панель",
            callback_data=AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL).pack(),
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def admin_main_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [admin_button("Управление библиотекой", AdminAction.MANAGE_LIBRARY)],
            [admin_button("Управление подписками", AdminAction.MANAGE_SUBSCRIBERS)],
            [admin_button("Выдать админку", AdminAction.APPOINT)],
            [
                admin_button("Запросы на возврат", AdminAction.VIEW_RETURN_REQUESTS),
                admin_button("Запросы на получение", AdminAction.VIEW_TAKE_REQUESTS),
            ],
            [admin_button("Создать рассылку", AdminAction.CREATE_NOTIFICATION)],
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
                admin_button("Статистика", AdminAction.VIEW_STATS)
            ],
            [
                return_button(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL))
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


def manage_subscriptions_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Выдать подписку",
                        callback_data=AdminCallback(action=AdminAction.GIVE_SUB).pack()
                    ),
                ],

                [
                    InlineKeyboardButton(
                        text="Удалить подписку",
                        callback_data=AdminCallback(action=AdminAction.REMOVE_SUBSCRIPTION).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Поменять тип подписки",
                        callback_data=AdminCallback(action=AdminAction.CHANGE_SUBSCRIPTION_TYPE).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Продлить подписку",
                        callback_data=AdminCallback(action=AdminAction.EXTEND_SUBSCRIPTION).pack()
                    )
                ],
                [
                    return_button(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL))
                ]

        ]
    )


def select_sub_plan_kb(sub_plans: List[Tuple[str, int]], is_new_plan = False) -> InlineKeyboardMarkup:
    action = AdminAction.SELECT_PLAN if not is_new_plan else AdminAction.SELECT_NEW_PLAN
    buttons = []
    for sub_plan in sub_plans:
        name = sub_plan[0]
        plan_id = sub_plan[1]
        buttons.append(
            [
                InlineKeyboardButton(
                    text=name,
                    callback_data=AdminCallback(action=action, plan_id=plan_id).pack()
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)



def confirm_remove_subscription_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, удалить подписку",
                    callback_data=AdminCallback(
                        action=AdminAction.CONFIRM_REMOVE_SUBSCRIPTION
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Нет, отменить",
                    callback_data=AdminCallback(
                        action=AdminAction.RETURN_TO_MAIN_PANEL
                    ).pack()
                )
            ]
        ]
    )

def confirm_change_plan_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Да, изменить тариф",
                        callback_data=AdminCallback(
                            action=AdminAction.CONFIRM_CHANGE_PLAN
                        ).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Нет, отменить",
                        callback_data=AdminCallback(
                            action=AdminAction.RETURN_TO_MAIN_PANEL
                        ).pack()
                    )
                ]
            ]
        )


def create_extend_options_kb() -> InlineKeyboardMarkup:
    """Создать клавиатуру с вариантами продления подписки"""
    buttons = [
        [
            InlineKeyboardButton(
                text="+1 месяц",
                callback_data=AdminCallback(
                    action=AdminAction.EXTEND_BY_MONTHS,
                    months=1
                ).pack()
            ),
            InlineKeyboardButton(
                text="+3 месяца",
                callback_data=AdminCallback(
                    action=AdminAction.EXTEND_BY_MONTHS,
                    months=3
                ).pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="+6 месяцев",
                callback_data=AdminCallback(
                    action=AdminAction.EXTEND_BY_MONTHS,
                    months=6
                ).pack()
            ),
            InlineKeyboardButton(
                text="+12 месяцев",
                callback_data=AdminCallback(
                    action=AdminAction.EXTEND_BY_MONTHS,
                    months=12
                ).pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="↩️ Назад",
                callback_data=AdminCallback(
                    action=AdminAction.RETURN_TO_MAIN_PANEL
                ).pack()
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)