from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from api import finance as finance_api
from api.client import ApiClient, ApiError
from callbacks.finance import PayoutCB
from filters.role import RoleFilter
from keyboards.inline.finance import payout_kb, review_teachers_kb
from states.payout import PartialPayout
from utils import labels as L
from utils.formatters import format_finance, format_payout_request, money
from utils.validators import parse_price_allow_zero

router = Router(name="admin_finance")
router.message.filter(RoleFilter("admin"))
router.callback_query.filter(RoleFilter("admin"))


@router.message(F.text == L.FINANCE)
async def finance_entry(message: Message, api: ApiClient):
    data = await finance_api.get_finance(api, message.from_user.id)
    await message.answer(format_finance(data), reply_markup=review_teachers_kb())


@router.callback_query(F.data == "finance_review")
async def review_teachers(cb: CallbackQuery, api: ApiClient):
    data = await finance_api.get_finance(api, cb.from_user.id)
    if not data["teachers"]:
        await cb.message.answer("Hozircha o'qituvchi yo'q.")
        await cb.answer()
        return
    for t in data["teachers"]:
        await cb.message.answer(format_payout_request(t), reply_markup=payout_kb(t["teacherId"]))
    await cb.answer()


@router.callback_query(PayoutCB.filter(F.action == "full"))
async def mark_full(cb: CallbackQuery, callback_data: PayoutCB, api: ApiClient):
    try:
        result = await finance_api.mark_payout_paid(api, cb.from_user.id, callback_data.teacher_id)
    except ApiError as e:
        await cb.answer(e.message, show_alert=True)
        return
    await cb.message.edit_text(f"{cb.message.html_text}\n\n✅ To'landi ({money(result['amountPaid'])})")
    await cb.answer()


@router.callback_query(PayoutCB.filter(F.action == "partial"))
async def ask_partial(cb: CallbackQuery, callback_data: PayoutCB, state: FSMContext):
    await state.set_state(PartialPayout.amount)
    await state.update_data(teacher_id=callback_data.teacher_id, chat_id=cb.message.chat.id, message_id=cb.message.message_id)
    await cb.message.answer("💬 O'qituvchi qancha summa to'laganini yozing (so'mda):")
    await cb.answer()


@router.message(PartialPayout.amount, F.text)
async def receive_partial(message: Message, state: FSMContext, api: ApiClient):
    amount = parse_price_allow_zero(message.text)
    if amount is None:
        await message.answer("Summani raqam bilan yozing. Masalan: <code>150000</code>")
        return

    data = await state.get_data()
    try:
        result = await finance_api.mark_payout_partial(api, message.from_user.id, data["teacher_id"], amount)
    except ApiError as e:
        await message.answer(e.message)
        await state.clear()
        return
    await state.clear()

    try:
        await message.bot.edit_message_reply_markup(chat_id=data["chat_id"], message_id=data["message_id"], reply_markup=None)
    except Exception:
        pass

    verdict = ("✅ To'liq to'landi" if result["status"] == "paid"
               else f"🟡 Qisman to'landi. Qarzi: {money(result['amountDue'] - result['amountPaid'])}")
    await message.answer(f"{verdict}\n💰 {money(result['amountPaid'])} / {money(result['amountDue'])}")