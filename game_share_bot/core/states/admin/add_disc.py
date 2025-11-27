from aiogram.fsm.state import State, StatesGroup


class AddDiscState(StatesGroup):
    waiting_for_id = State()
    waiting_for_confirmation = State()
