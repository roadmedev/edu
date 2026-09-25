from aiogram.fsm.state import State, StatesGroup


class PartialPayout(StatesGroup):
    amount = State()