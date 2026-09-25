from aiogram.fsm.state import State, StatesGroup


class PartialPayment(StatesGroup):
    amount = State()