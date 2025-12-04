from aiogram.fsm.state import State, StatesGroup


class RegisterState(StatesGroup):
    waiting_for_phone = State()


class TakeDiscState(StatesGroup):
    """Состояние для подтверждения взятия диска"""
    waiting_for_confirmation = State()

