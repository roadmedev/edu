from keyboards.reply.admin import admin_menu
from keyboards.reply.student import student_menu
from keyboards.reply.teacher import teacher_menu
from keyboards.reply.user import user_menu

_MENUS = {
    "admin": admin_menu,
    "teacher": teacher_menu,
    "student": student_menu,
    "user": user_menu,
}


def main_menu(role: str):
    return _MENUS.get(role, user_menu)()