# keyboards/teachers_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_teachers_keyboard(teachers: list[dict]) -> InlineKeyboardMarkup:
    """O'qituvchilar ro'yxati + qo'shish tugmasi"""
    buttons = [
        [
            InlineKeyboardButton(
                text=f"👨‍🏫 {t['full_name']}",
                callback_data=f"teacher:{t['id']}",
            )
        ]
        for t in teachers
    ]

    buttons.append([
        InlineKeyboardButton(
            text="➕ Yangi o'qituvchi qo'shish",
            callback_data="admin_teacher:add",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_teacher_detail_keyboard(teacher_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Tahrirlash",
                    callback_data=f"teacher_edit:{teacher_id}",
                ),
                InlineKeyboardButton(
                    text="🗑 O'chirish",
                    callback_data=f"teacher_delete:{teacher_id}",
                ),
            ],
        ]
    )


def get_edit_field_keyboard(teacher_id: int) -> InlineKeyboardMarkup:
    fields = [
        ("Ism", "full_name"),
        ("Daraja", "degree"),
        ("Sertifikat", "certificate_info"),
        ("Maosh", "salary"),
    ]
    buttons = [
        [
            InlineKeyboardButton(
                text=f"✏️ {label}",
                callback_data=f"teacher_edit_field:{teacher_id}:{field}",
            )
        ]
        for label, field in fields
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_delete_confirm_keyboard(teacher_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ha, o'chirilsin",
                    callback_data=f"teacher_delete_confirm:{teacher_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data="teacher_delete_cancel",
                ),
            ]
        ]
    )


def get_profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="profile_edit"),
            ],
            [
                InlineKeyboardButton(text="➕ Yangi kurs qo'shish", callback_data="course_add"),
            ],
        ]
    )


def get_edit_field_keyboard() -> InlineKeyboardMarkup:
    fields = [
        ("Ism", "full_name"),
        ("Daraja", "degree"),
        ("Sertifikat", "certificate_info"),
        ("Rasm URL", "photo_url"),
    ]
    buttons = [
        [InlineKeyboardButton(text=f"✏️ {label}", callback_data=f"profile_edit_field:{field}")]
        for label, field in fields
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_courses_list_keyboard(courses: list[dict]) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f"📚 {c['title']} ({c.get('students_count', 0)} o'quvchi)",
                callback_data=f"my_course:{c['id']}",
            )
        ]
        for c in courses
    ]
    buttons.append([
        InlineKeyboardButton(text="➕ Yangi kurs qo'shish", callback_data="course_add")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_course_detail_keyboard(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🕐 Dars jadvali",
                    callback_data=f"course_schedule:{course_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="➕ Jadval qo'shish",
                    callback_data=f"schedule_add:{course_id}",
                ),
                InlineKeyboardButton(
                    text="🗑 Kursni o'chirish",
                    callback_data=f"course_delete:{course_id}",
                ),
            ],
        ]
    )