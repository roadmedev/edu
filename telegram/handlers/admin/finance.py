# handlers/admin/finance.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from services.admin_service import (
    get_finance_summary,
    get_finance_history,
    get_finance_shares,
)
from keyboards.finance_kb import get_finance_keyboard
from utils.filters import IsAdmin

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


def format_money(amount) -> str:
    try:
        return f"{int(float(amount)):,}".replace(",", " ")
    except (ValueError, TypeError):
        return str(amount)


@router.message(F.text == "💰 Moliya")
async def show_finance(message: Message) -> None:
    data = await get_finance_summary()

    if "error" in data:
        await message.answer("⚠️ Moliyani yuklashda xatolik.")
        return

    text = (
        f"💰 <b>Moliya bo'limi</b> (joriy oy)\n\n"
        f"📥 Kirim: <b>{format_money(data['income'])} so'm</b>\n"
        f"📤 Chiqim: <b>{format_money(data['expense'])} so'm</b>\n"
        f"💵 Sof foyda: <b>{format_money(data['net_profit'])} so'm</b>\n"
        f"⚠️ Qarzdorlik: <b>{format_money(data['debt'])} so'm</b>\n\n"
        f"🏦 <b>Markaz ulushi (30%): {format_money(data.get('admin_share', 0))} so'm</b>"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=get_finance_keyboard())


@router.callback_query(F.data.startswith("finance_history:"))
async def show_finance_history(callback: CallbackQuery) -> None:
    history_type = callback.data.split(":")[1]
    result = await get_finance_history(history_type)
    history = result.get("history", [])

    label = "📥 Kirimlar" if history_type == "income" else "📤 Chiqimlar"

    if not history:
        await callback.message.answer(f"{label} tarixi topilmadi.")
        await callback.answer()
        return

    lines = [f"• {row['month']} — <b>{format_money(row['total'])} so'm</b>" for row in history]
    text = f"<b>{label} tarixi (oxirgi 6 oy)</b>\n\n" + "\n".join(lines)

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "finance_shares")
async def show_shares(callback: CallbackQuery) -> None:
    """Har bir o'qituvchi bo'yicha 30% ulush hisoboti"""
    result = await get_finance_shares()

    if "error" in result:
        await callback.answer("Xatolik", show_alert=True)
        return

    teachers = result.get("teachers", [])
    current = result.get("current_month", {})

    if not teachers:
        await callback.message.answer("Hozircha ma'lumot yo'q.")
        await callback.answer()
        return

    lines = []
    for t in teachers[:20]:
        lines.append(
            f"👨‍🏫 <b>{t['teacher_name']}</b>\n"
            f"   📅 {t['month']}\n"
            f"   💵 Daromad: {format_money(t['gross_income'])} so'm\n"
            f"   🏦 Ulush (30%): <b>{format_money(t['admin_share'])} so'm</b>"
        )

    text = f"<b>🏦 Markaz ulushi (30%)</b>\n\n" + "\n\n".join(lines)

    if current:
        text += (
            f"\n\n━━━━━━━━━━━━━━━━━━\n"
            f"<b>Joriy oy jami:</b>\n"
            f"💵 {format_money(current.get('total_gross', 0))} so'm\n"
            f"🏦 Ulush: <b>{format_money(current.get('total_admin', 0))} so'm</b>"
        )

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()