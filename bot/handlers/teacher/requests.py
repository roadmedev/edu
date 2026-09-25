from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery

from api import enrollments as enr_api
from api.client import ApiClient, ApiError
from callbacks.enrollments import EnrollCB
from filters.role import RoleFilter
from keyboards.inline.enrollments import terms_kb
from utils.texts import REJECTED, student_accepted

router = Router(name="teacher_requests")
router.callback_query.filter(RoleFilter("teacher"))


@router.callback_query(EnrollCB.filter(F.action.in_({"accept", "reject"})))
async def decide(cb: CallbackQuery, callback_data: EnrollCB, api: ApiClient):
    try:
        d = await enr_api.decide(api, cb.from_user.id, callback_data.enrollment_id, callback_data.action)
    except ApiError as e:
        text = e.message if 400 <= e.status < 500 else "Xatolik yuz berdi, keyinroq urinib ko'ring."
        await cb.answer(text, show_alert=True)
        if e.status == 409:  # allaqachon hal qilingan, tugmalarni olib tashlaymiz
            await cb.message.edit_reply_markup(reply_markup=None)
        return

    accepted = callback_data.action == "accept"
    verdict = "✅ Qabul qilindi" if accepted else "❌ Rad etildi"
    await cb.message.edit_text(f"{cb.message.html_text}\n\n<b>{verdict}</b>", reply_markup=None)

    try:
        if accepted:
            await cb.bot.send_message(d["studentTgId"], student_accepted(d), reply_markup=terms_kb(d["id"]))
        else:
            await cb.bot.send_message(d["studentTgId"], REJECTED)
    except TelegramAPIError:
        await cb.message.answer("⚠️ Qaror saqlandi, lekin o'quvchiga xabar yetkazib bo'lmadi.")
    await cb.answer()