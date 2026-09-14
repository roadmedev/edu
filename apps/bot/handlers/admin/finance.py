from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from services.finance_service import get_finance_summary, get_finance_history
from keyboards.finance_kb import get_finance_keyboard

router = Router()


@router.message(F.text == "💰 Moliya bo'limi")
async def show_finance(message: Message) -> None:
    data = await get_finance_summary()

    if "error" in data:
        await message.answer("Moliya ma'lumotlarini yuklashda xatolik yuz berdi.")
        return

    text = (
        f"💰 <b>Moliya bo'limi</b> (joriy oy)\n\n"
        f"Kirim — {data['income']} so'm\n"
        f"Chiqim — {data['expense']} so'm\n"
        f"Sof foyda — {data['net_profit']} so'm\n"
        f"Qarzdorlik — {data['debt']} so'm"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=get_finance_keyboard())


@router.callback_query(F.data.startswith("finance_history:"))
async def show_finance_history(callback: CallbackQuery) -> None:
    history_type = callback.data.split(":")[1]
    result = await get_finance_history(history_type)
    history = result.get("history", [])

    label = "Kirimlar" if history_type == "income" else "Chiqimlar"

    if not history:
        await callback.message.answer(f"{label} tarixi topilmadi.")
        await callback.answer()
        return

    lines = [f"{row['month']} — {row['total']} so'm" for row in history]
    text = f"📊 <b>{label} tarixi (oxirgi 6 oy)</b>\n\n" + "\n".join(lines)

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()