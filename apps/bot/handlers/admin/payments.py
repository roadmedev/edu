from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from services.payments_service import get_paid_students, get_debtors
from keyboards.payments_kb import get_payments_menu

router = Router()


@router.message(F.text == "💳 To'lovlar")
async def show_payments_menu(message: Message) -> None:
    await message.answer(
        "Qaysi ro'yxatni ko'rmoqchisiz?",
        reply_markup=get_payments_menu(),
    )


@router.callback_query(F.data == "payments:paid")
async def show_paid(callback: CallbackQuery) -> None:
    students = await get_paid_students()

    if not students:
        await callback.message.answer("Bu oy hali hech kim to'lov qilmagan.")
        await callback.answer()
        return

    lines = [f"✅ {s['full_name']} — {s['amount']} so'm" for s in students]
    text = "<b>To'lov qilganlar (joriy oy):</b>\n\n" + "\n".join(lines)

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "payments:debtors")
async def show_debtors(callback: CallbackQuery) -> None:
    students = await get_debtors()

    if not students:
        await callback.message.answer("Hozircha qarzdorlar yo'q. 🎉")
        await callback.answer()
        return

    lines = [
        f"❗ {s['full_name']} — {s['course_title']} ({s['price']} so'm)"
        for s in students
    ]
    text = "<b>Qarzdorlar:</b>\n\n" + "\n".join(lines)

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()