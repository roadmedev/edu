from aiogram.fsm.state import State, StatesGroup


class AddTeacher(StatesGroup):
    waiting_for_name = State()
    waiting_for_degree = State()
    waiting_for_subject = State()
    waiting_for_certificate = State()
    waiting_for_salary = State()


class EditTeacher(StatesGroup):
    waiting_for_new_value = State()