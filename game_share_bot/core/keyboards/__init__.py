from .inline.admin import admin_kb, return_to_admin_panel_kb, rental_actions_confirmation_kb, add_game_image_kb
from .inline.common import return_kb, confirmation_kb
from .inline.game import enter_queue_kb
from .inline.menu import main_menu_kb, personal_cabinet_kb, rentals_kb, catalog_keyboard
from .inline.subscription import subscription_actions_kb, select_duration_kb, confirm_subscription_buy_kb
from .inline.buttons import return_button
from .reply.register import register_kb

__all__ = [
    'main_menu_kb',
    'return_kb',
    'register_kb',
    'enter_queue_kb',
    'admin_kb',
    'confirmation_kb',
    'add_game_image_kb',
    'return_to_admin_panel_kb',
    'personal_cabinet_kb',
    'rentals_kb',
    'select_duration_kb',
    'confirm_subscription_buy_kb',
    'subscription_actions_kb',
    'rental_actions_confirmation_kb',
    'return_button',
    'catalog_keyboard'
]
