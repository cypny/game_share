from .admin.admin import router as admin_router
from .admin.appoint import router as admin_appoint_router
from .debug import router as debug_router
from .games.catalog import router as catalog_router
from .games.game import router as game_router
from .menu.main import router as main_menu_router
from .start import router as start_router

routers = [
    admin_router,
    debug_router,
    main_menu_router,
    start_router,
    catalog_router,
    game_router,
    admin_appoint_router
]

__all__ = ['routers']
