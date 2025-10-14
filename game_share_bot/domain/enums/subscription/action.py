from enum import StrEnum


class SubscriptionAction(StrEnum):
    INFO = "info"
    SELECT_DURATION = "select_duration"
    CONFIRM_BUY = "confirm_buy"
    BUY = "buy"