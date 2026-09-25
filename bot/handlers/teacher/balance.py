from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from api import courses as courses_api, payments as payments_api, students as students_api, teachers as teachers_api
from api.client import ApiClient, ApiError
from callbacks.payments import PayCB
from filters.role import RoleFilter
from keyboards.inline.payments import payment_request_kb, review_students_kb
from states.payment import PartialPayment
from utils import labels as L
from utils.formatters import format_balance, format_payment_request, money
from utils.validators import parse_price_allow_zero

router = Router(name="teacher_balance")
router.message.filter(RoleFilter("teacher"))
router.callback_query.filter(RoleFilter("teacher"))


@router.message(F.text == L.BALANCE)
async def balance_entry(message: Message, api: ApiClient):
    balance = await teachers_api.get_balance(api, message.from_user.id)
    await message.answer(format_balance(balance), reply_markup=review_students_kb())


@router.callback_query(F.data == "balance_review")
async def review_students(cb: CallbackQuery, api: ApiClient):
    courses = await courses_api.my_courses(api, cb.from_user.id)
    sent_any = False
    for c in courses:
        data = await students_api.course_students(api, cb.from_user.id, c["id"])
        if not data["students"]:
            continue
        sent_any = True
        await cb.message.answer(f"📚 <b>{escape(c['title'])}</b>")
        for s in data["students"]:
            await cb.message.answer(format_payment_request(s), reply_markup=payment_request_kb(s["enrollmentId"]))
    if not sent_any:
        await cb.message.answer("Hozircha faol o'quvchi yo'q.")
    await cb.answer()


@router.callback_query(PayCB.filter(F.action == "full"))
async def bulk_mark_paid(cb: CallbackQuery, callback_data: PayCB, api: ApiClient):
    try:
        result = await payments_api.mark_paid(api, cb.from_user.id, callback_data.enrollment_id)
    except ApiError as e:
        await cb.answer(e.message, show_alert=True)
        return
    await cb.message.edit_text(f"{cb.message.html_text}\n\n✅ To'landi ({money(result['payment']['amountPaid'])})")
    await cb.answer()


@router.callback_query(PayCB.filter(F.action == "partial"))
async def ask_partial(cb: CallbackQuery, callback_data: PayCB, state: FSMContext):
    await state.set_state(PartialPayment.amount)
    await state.update_data(
        enrollment_id=callback_data.enrollment_id,
        chat_id=cb.message.chat.id,
        message_id=cb.message.message_id,
    )
    await cb.message.answer("💬 Qancha summa to'laganini yozing (so'mda). Masalan: <code>200000</code>")
    await cb.answer()


@router.message(PartialPayment.amount, F.text)
async def receive_partial_amount(message: Message, state: FSMContext, api: ApiClient):
    amount = parse_price_allow_zero(message.text)
    if amount is None:
        await message.answer("Summani raqam bilan yozing. Masalan: <code>200000</code>")
        return

    data = await state.get_data()
    try:
        result = await payments_api.mark_partial(api, message.from_user.id, data["enrollment_id"], amount)
    except ApiError as e:
        await message.answer(e.message)
        await state.clear()
        return
    await state.clear()

    try:
        await message.bot.edit_message_reply_markup(
            chat_id=data["chat_id"], message_id=data["message_id"], reply_markup=None,
        )
    except Exception:
        pass

    p = result["payment"]
    verdict = "✅ To'liq to'landi" if p["status"] == "paid" else f"🟡 Qisman to'landi. Qarzi: {money(p['amountDue'] - p['amountPaid'])}"
    await message.answer(
        f"{verdict}\n👤 <b>{escape(result['studentName'])}</b>: {money(p['amountPaid'])} / {money(p['amountDue'])}"
    )