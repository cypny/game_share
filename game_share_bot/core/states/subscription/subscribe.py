from aiogram.fsm.state import StatesGroup, State


class SubscriptionState(StatesGroup):
    choosing_plan = State()
    choosing_duration = State()
    confirming = State()