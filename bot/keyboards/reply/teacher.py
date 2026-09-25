from keyboards.reply.common import build
from utils import labels as L


def teacher_menu():
    return build((L.MY,), (L.MY_STUDENTS, L.BALANCE), (L.SUGGEST,))

def teacher_my_menu():
    return build((L.NEW_COURSE, L.SCHEDULE), (L.BACK,))