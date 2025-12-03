from aiogram.fsm.state import State, StatesGroup


class CreateNotificationState(StatesGroup):
    waiting_for_message = State()
