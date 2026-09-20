# handlers/teacher/menu.py
from aiogram import Router, F
from aiogram.types import Message

from keyboards.teacher_menu import get_teacher_menu
from utils.filters import IsTeacher

router = Router()

router.message.filter(IsTeacher())
router.callback_query.filter(IsTeacher())


@router.message(F.text == "🏠 Asosiy menyu")
async def back_to_teacher_menu(message: Message) -> None:
    await message.answer(
        "🏠 Asosiy menyu:",
        reply_markup=get_teacher_menu(),
    )