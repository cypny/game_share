from aiogram.fsm.state import State, StatesGroup


class AddGameState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_image = State()
    waiting_for_confirmation = State()