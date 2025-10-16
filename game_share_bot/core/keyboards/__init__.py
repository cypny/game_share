from .inline.admin import admin_kb
from .inline.admin import admin_kb, return_to_admin_panel_kb, returns_confirmation_kb
from .inline.common import return_kb, confirmation_kb
from .inline.game import add_game_image_kb, get_game_detail_kb
from .inline.menu import main_menu_kb, personal_cabinet_kb, rentals_kb
from .inline.subscription import subscription_actions_kb, select_duration_kb, confirm_subscription_buy_kb
from .reply.register import register_kb

__all__ = [
    'main_menu_kb',
    'return_kb',
    'register_kb',
    'get_game_detail_kb',
    'admin_kb',
    'confirmation_kb',
    'add_game_image_kb',
    'return_to_admin_panel_kb',
    'personal_cabinet_kb',
    'rentals_kb',
    'select_duration_kb',
    'confirm_subscription_buy_kb',
    'subscription_actions_kb',
    'returns_confirmation_kb'
]
