# states/teacher_schedule.py
from aiogram.fsm.state import State, StatesGroup


class AddSchedule(StatesGroup):
    waiting_for_day = State()
    waiting_for_start = State()
    waiting_for_end = State()
    waiting_for_more = State()