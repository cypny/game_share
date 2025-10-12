from enum import StrEnum


class AdminAction(StrEnum):
    ADD_GAME = "add_game"
    DELETE_GAME = "delete_game"
    APPOINT = "appoint"
    RETURN_TO_MAIN_PANEL = "return_to_main_panel"
    SKIP_IMAGE_INPUT = "skip_image_input"