from aiogram.fsm.state import State, StatesGroup

class BroadcastStates(StatesGroup):
    text = State()
    confirm = State()