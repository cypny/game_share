from .debug import router as debug_router
from .games.catalog import router as catalog_router
from .menu import router as menu_router
from .start import router as start_router
from .user import router as user_router

routers = [
    debug_router,
    menu_router,
    start_router,
    user_router,
    catalog_router
]
