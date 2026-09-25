from aiogram.fsm.state import State, StatesGroup


class SuggestionStates(StatesGroup):
    text = State()