from aiogram.fsm.state import State, StatesGroup


class GiveSubState(StatesGroup):
    waiting_for_duration = State()
