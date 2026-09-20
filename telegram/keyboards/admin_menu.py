# keyboards/admin_menu.py
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_admin_menu() -> ReplyKeyboardMarkup:
    """Admin asosiy menyusi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Markaz statistikasi")],
            [
                KeyboardButton(text="👥 Foydalanuvchilar"),
                KeyboardButton(text="💰 Moliya"),
            ],
            [KeyboardButton(text="💡 Taklif qutisi")],
        ],
        resize_keyboard=True,
    )


def get_users_submenu() -> ReplyKeyboardMarkup:
    """Foydalanuvchilar bo'limi (asosiy menyu o'zgaradi)"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Oddiy foydalanuvchilar")],
            [
                KeyboardButton(text="👨‍🏫 O'qituvchilar"),
                KeyboardButton(text="🎓 O'quvchilar"),
            ],
            [KeyboardButton(text="🔙 Orqaga")],
        ],
        resize_keyboard=True,
    )


def get_teachers_actions() -> InlineKeyboardMarkup:
    """O'qituvchilar ro'yxati ustidagi inline tugmalar"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Yangi o'qituvchi qo'shish",
                    callback_data="admin_teacher:add",
                )
            ],
        ]
    )