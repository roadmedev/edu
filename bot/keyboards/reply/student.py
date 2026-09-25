from keyboards.reply.common import build
from utils import labels as L


def student_menu():
    return build((L.COURSES,), (L.MY, L.SCHEDULE, L.RATING), (L.HELP,))