from .admin.appoint import router as admin_appoint_router
from .admin.main_panel import router as admin_main_panel_router
from .admin.manage_library.add_game import router as admin_add_game_router
from .admin.manage_library.delete_game import router as admin_delete_game_router
from .admin.manage_library.add_disc import router as admin_add_disc_router
from .admin.manage_library.delete_disc import router as admin_delete_disc_router
from .admin.manage_library.manage_library import router as admin_manage_library_panel_router
from .admin.manage_subscribers import router as admin_manage_subscribers_router
from .admin.return_requests import router as admin_return_requests_router
from .admin.notify_actions import router as admin_notify_actions_router
from .debug import router as debug_router
from .games.catalog import router as catalog_router
from .games.game import router as game_router
from .menu.main import router as main_menu_router
from .menu.personal_cabinet import router as personal_cabinet_router
from .menu.rented_disks import router as rented_disks_router
from .start import router as start_router
from .user.queue import router as queue_router
from .user.subscription import router as user_subscription_router
from .user.rental_history import router as rental_history_router
from .admin.stats import router as admin_stats_router

routers = [
    # Админ панель
    admin_main_panel_router,
    admin_manage_library_panel_router,
    admin_manage_subscribers_router,
    admin_appoint_router,
    admin_add_game_router,
    admin_delete_game_router,
    admin_add_disc_router,
    admin_delete_disc_router,
    admin_return_requests_router,
    admin_stats_router,
    admin_notify_actions_router,

    # Стартовые и основные
    start_router,
    main_menu_router,

    # Каталог игр
    game_router,

    # Личный кабинет
    personal_cabinet_router,
    rented_disks_router,
    rental_history_router,

    # Подписки и очередь
    user_subscription_router,
    queue_router,

    # Отладка
    debug_router,

    # В конец чтобы работало
    catalog_router,
]


__all__ = ['routers']
