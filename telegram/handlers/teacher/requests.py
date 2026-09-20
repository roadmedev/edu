# handlers/teacher/requests.py
from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.teacher_service import get_teacher_requests, respond_to_request
from keyboards.requests_kb import get_request_actions_keyboard
from utils.filters import IsTeacher

router = Router()
router.callback_query.filter(IsTeacher())


# ⚠️ Bu handler User panelida "Kursga qo'shilish" bosilganda ishga tushadi
# Teacher'ga so'rov kelganda — inline tugmalar orqali javob beradi


@router.callback_query(F.data.startswith("req_accept:"))
async def accept_request(callback: CallbackQuery) -> None:
    request_id = int(callback.data.split(":")[1])

    result = await respond_to_request(request_id, "accepted")

    if "error" in result:
        await callback.answer(f"Xatolik: {result['error']}", show_alert=True)
        return

    await callback.message.edit_text(
        "✅ So'rov qabul qilindi.\n"
        "Foydalanuvchiga xabar yuborildi."
    )
    await callback.answer("Qabul qilindi")


@router.callback_query(F.data.startswith("req_reject:"))
async def reject_request(callback: CallbackQuery) -> None:
    request_id = int(callback.data.split(":")[1])

    result = await respond_to_request(
        request_id,
        "rejected",
        rejection_reason="Kurs to'lgan yoki o'qituvchi rad etdi",
    )

    if "error" in result:
        await callback.answer(f"Xatolik: {result['error']}", show_alert=True)
        return

    await callback.message.edit_text(
        "❌ So'rov rad etildi.\n"
        "Foydalanuvchiga xabar yuborildi."
    )
    await callback.answer("Rad etildi")