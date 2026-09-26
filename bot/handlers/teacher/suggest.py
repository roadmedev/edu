from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from api import suggestions as suggestions_api
from api.client import ApiClient, ApiError
from filters.role import RoleFilter
from states.suggestion import SuggestionStates
from utils import labels as L

router = Router(name="teacher_suggest")
router.message.filter(RoleFilter("teacher"))


@router.message(F.text == L.SUGGEST)
async def ask_suggestion(message: Message, state: FSMContext):
    await state.set_state(SuggestionStates.text)
    await message.answer("💡 Taklifingizni yozing:")


@router.message(SuggestionStates.text, F.text)
async def receive_suggestion(message: Message, state: FSMContext, api: ApiClient):
    text = message.text.strip()
    if not 3 <= len(text) <= 500:
        await message.answer("Taklif matni 3 tadan 500 tagacha belgida bo'lsin:")
        return

    try:
        await suggestions_api.send_suggestion(api, message.from_user.id, text)
    except ApiError as e:
        await message.answer(f"⚠️ Xatolik: {e.message}")
        return

    await state.clear()
    await message.answer("✅ Taklifingiz uchun rahmat! Administratorga yetkazildi.")