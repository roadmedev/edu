# handlers/teacher/suggestions.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.teacher_service import send_suggestion
from states.suggestion import SuggestionState
from utils.filters import IsTeacher

router = Router()
router.message.filter(IsTeacher())


@router.message(F.text == "💡 Taklif")
async def start_suggestion(message: Message, state: FSMContext) -> None:
    await state.set_state(SuggestionState.waiting_for_message)
    await message.answer(
        "💡 Taklifingizni yozing:\n\n"
        "(Bekor qilish uchun /cancel)"
    )


@router.message(SuggestionState.waiting_for_message)
async def save_suggestion(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Bekor qilindi.")
        return

    result = await send_suggestion(message.from_user.id, message.text)
    await state.clear()

    if "error" in result:
        await message.answer("⚠️ Xatolik yuz berdi.")
        return

    await message.answer("✅ Taklifingiz adminga yuborildi. Rahmat!")