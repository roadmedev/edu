from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_teachers_keyboard(teachers: list[dict]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=t["full_name"], callback_data=f"teacher:{t['id']}")]
        for t in teachers
    ]
    buttons.append([InlineKeyboardButton(text="➕ Yangi o'qituvchi qo'shish", callback_data="teacher_add")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_teacher_detail_keyboard(teacher_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"teacher_edit:{teacher_id}"),
                InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"teacher_delete:{teacher_id}"),
            ]
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
        [InlineKeyboardButton(text=label, callback_data=f"teacher_edit_field:{teacher_id}:{field}")]
        for label, field in fields
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_delete_confirm_keyboard(teacher_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, o'chirilsin", callback_data=f"teacher_delete_confirm:{teacher_id}"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="teacher_delete_cancel"),
            ]
        ]
    )