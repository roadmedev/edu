# states/suggestion.py
from aiogram.fsm.state import State, StatesGroup


class SuggestionState(StatesGroup):
    waiting_for_message = State()