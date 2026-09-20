# states/teacher_course.py
from aiogram.fsm.state import State, StatesGroup


class EditProfile(StatesGroup):
    waiting_for_new_value = State()


class AddCourse(StatesGroup):
    waiting_for_photo = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_price = State()