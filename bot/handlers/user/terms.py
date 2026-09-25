from html import escape

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery

from api import enrollments as enr_api
from api.client import ApiClient, ApiError
from callbacks.enrollments import EnrollCB
from filters.role import RoleFilter
from keyboards.reply.menu import main_menu

router = Router(name="user_terms")
router.callback_query.filter(RoleFilter("user", "student"))


@router.callback_query(EnrollCB.filter(F.action == "terms"))
async def accept_terms(cb: CallbackQuery, callback_data: EnrollCB, api: ApiClient):
    try:
        d = await enr_api.accept_terms(api, cb.from_user.id, callback_data.enrollment_id)
    except ApiError as e:
        text = e.message if 400 <= e.status < 500 else "Xatolik yuz berdi, keyinroq urinib ko'ring."
        await cb.answer(text, show_alert=True)
        if e.status == 409:
            await cb.message.edit_reply_markup(reply_markup=None)
        return

    await cb.message.edit_reply_markup(reply_markup=None)
    # `user` middleware'dan eski rol bilan keladi, shuning uchun student menyusini to'g'ridan-to'g'ri beramiz
    await cb.message.answer(
        f"🎉 Tabriklaymiz! Siz «{escape(d['courseTitle'])}» kursining o'quvchisisiz.\n"
        "Endi sizga yangi bo'limlar ochildi 👇",
        reply_markup=main_menu("student"),
    )

    try:
        await cb.bot.send_message(
            d["teacherTgId"],
            f"🎓 <b>{escape(d['studentName'])}</b> shartlarni qabul qildi va «{escape(d['courseTitle'])}» kursiga qo'shildi.",
        )
    except TelegramAPIError:
        pass
    await cb.answer()