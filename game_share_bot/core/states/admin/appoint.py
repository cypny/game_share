from aiogram.fsm.state import State, StatesGroup


class AppointState(StatesGroup):
    waiting_for_tg_id = State()
