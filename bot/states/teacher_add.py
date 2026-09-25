from aiogram.fsm.state import State, StatesGroup


class TeacherAdd(StatesGroup):
    photo = State()
    subject = State()
    certificate = State()