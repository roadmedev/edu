from keyboards.reply.common import build
from utils import labels as L


def admin_menu():
    return build((L.STATS,), (L.USERS, L.FINANCE), (L.SUGGESTION_BOX,))


def admin_users_menu():
    return build((L.PLAIN_USERS,), (L.TEACHERS, L.STUDENTS_LIST), (L.BACK,))