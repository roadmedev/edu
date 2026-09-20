from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from services.payments_service import get_paid_students, get_debtors, mark_paid
from keyboards.payments_kb import get_payments_menu, get_debtors_keyboard

router = Router()


@router.message(F.text == "💳 To'lovlar")
async def show_payments_menu(message: Message) -> None:
    await message.answer("Qaysi ro'yxatni ko'rmoqchisiz?", reply_markup=get_payments_menu())


@router.callback_query(F.data == "payments:paid")
async def show_paid(callback: CallbackQuery) -> None:
    students = await get_paid_students()

    if not students:
        await callback.message.answer("Bu oy hali hech kim to'lov qilmagan.")
        await callback.answer()
        return

    lines = [f"✅ {s['full_name']} — {s['amount']} so'm" for s in students]
    await callback.message.answer(
        "<b>To'lov qilganlar (joriy oy):</b>\n\n" + "\n".join(lines),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "payments:debtors")
async def show_debtors(callback: CallbackQuery) -> None:
    debtors = await get_debtors()

    if not debtors:
        await callback.message.answer("Hozircha qarzdorlar yo'q. 🎉")
        await callback.answer()
        return

    await callback.message.answer(
        "Qarzdorlar ro'yxati (bosing — to'lovni qayd etadi):",
        reply_markup=get_debtors_keyboard(debtors),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("mark_paid:"))
async def handle_mark_paid(callback: CallbackQuery) -> None:
    enrollment_id = callback.data.split(":")[1]
    result = await mark_paid(enrollment_id)

    if "error" in result:
        await callback.answer("Xatolik yuz berdi, qayta urinib ko'ring.", show_alert=True)
        return

    await callback.answer("✅ To'lov qayd etildi!", show_alert=True)
    await callback.message.answer("To'lov muvaffaqiyatli qayd etildi. ✅")