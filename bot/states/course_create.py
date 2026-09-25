from aiogram.fsm.state import State, StatesGroup


class CourseCreate(StatesGroup):
    photo = State()
    title = State()
    description = State()
    price = State()
    certificate = State()
    day = State()            # kun tanlash
    start = State()          # boshlanish vaqti
    end = State()            # tugash vaqti
    schedule_menu = State()  # "kun qo'shish / saqlash / bekor" tugmalari kutilmoqda