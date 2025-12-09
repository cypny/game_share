from aiogram.fsm.state import State, StatesGroup


class ManageSubscribersState(StatesGroup):
    waiting_for_user_phone = State()
