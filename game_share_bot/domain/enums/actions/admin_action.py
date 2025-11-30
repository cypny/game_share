from enum import StrEnum


class AdminAction(StrEnum):
    """Действия администратора"""
    ADD_GAME = "add_game"
    DELETE_GAME = "delete_game"
    APPOINT = "appoint"
    RETURN_TO_MAIN_PANEL = "return_to_main_panel"
    SKIP_IMAGE_INPUT = "skip_image_input"
    VIEW_RETURN_REQUESTS = "view_return_requests"
    CREATE_NOTIFICATION = "create_notification"
    SEND_NOTIFICATION_TO_ALL = "send_notification_to_all"
    SEND_NOTIFICATION_TO_ACTIVE = "send_notification_to_active"