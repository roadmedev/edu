from html import escape

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from api import courses as courses_api
from api.client import ApiClient, ApiError
from callbacks.teacher import DayCB, FlowCB
from filters.role import RoleFilter
from keyboards.inline.teacher import (
    cancel_kb, conflict_kb, days_kb, schedule_actions_kb, skip_cert_kb,
)
from keyboards.reply.teacher import teacher_my_menu
from states.course_create import CourseCreate
from utils import labels as L
from utils.formatters import WEEKDAYS, format_timetable, money
from utils.validators import parse_price, parse_time

router = Router(name="teacher_course_create")
router.message.filter(RoleFilter("teacher"))
router.callback_query.filter(RoleFilter("teacher"))


def _day(n: int) -> str:
    return WEEKDAYS[n].capitalize()


def _draft_text(slots: list[dict]) -> str:
    lines = [f"• {_day(s['weekday'])}: {s['startTime']}–{s['endTime']}"
             for s in sorted(slots, key=lambda s: s["weekday"])]
    return "✅ Qo'shildi.\n\n<b>Kurs jadvali:</b>\n" + "\n".join(lines)


async def _show_day_picker(message: Message, state: FSMContext, edit: bool):
    data = await state.get_data()
    taken = {s["weekday"] for s in data.get("slots", [])}
    await state.set_state(CourseCreate.day)
    text = "6/6. 🗓 Dars haftaning qaysi kuni bo'ladi?"
    if edit:
        await message.edit_text(text, reply_markup=days_kb(taken))
    else:
        await message.answer(text, reply_markup=days_kb(taken))


# ---------- Boshlash va bekor qilish ----------
@router.message(F.text == L.NEW_COURSE)
async def start_create(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(CourseCreate.photo)
    await message.answer("🆕 <b>Yangi kurs</b>\n\n1/6. Kurs uchun <b>rasm</b> yuboring:", reply_markup=cancel_kb())


@router.callback_query(FlowCB.filter(F.action == "cancel"))
async def cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("❌ Bekor qilindi.")
    await cb.answer()


@router.callback_query(FlowCB.filter(F.action == "timetable"))
async def timetable(cb: CallbackQuery, api: ApiClient):
    await cb.message.answer(format_timetable(await courses_api.list_courses(api)))
    await cb.answer()


# ---------- 1-5: kurs ma'lumotlari ----------
@router.message(CourseCreate.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(CourseCreate.title)
    await message.answer("2/6. <b>Kurs nomini</b> yozing:", reply_markup=cancel_kb())


@router.message(CourseCreate.photo)
async def photo_invalid(message: Message):
    await message.answer("Iltimos, rasmni oddiy rasm sifatida yuboring (fayl emas).")


@router.message(CourseCreate.title, F.text)
async def get_title(message: Message, state: FSMContext):
    title = " ".join(message.text.split())
    if not 3 <= len(title) <= 100:
        await message.answer("Kurs nomi 3 tadan 100 tagacha belgi bo'lsin:")
        return
    await state.update_data(title=title)
    await state.set_state(CourseCreate.description)
    await message.answer("3/6. Kurs bo'yicha <b>tavsif</b> yozing (nimalar o'rgatiladi):", reply_markup=cancel_kb())


@router.message(CourseCreate.description, F.text)
async def get_description(message: Message, state: FSMContext):
    text = message.text.strip()
    if not 10 <= len(text) <= 600:
        await message.answer("Tavsif 10 tadan 600 tagacha belgi bo'lsin:")
        return
    await state.update_data(description=text)
    await state.set_state(CourseCreate.price)
    await message.answer("4/6. Kursning <b>oylik narxini</b> so'mda yozing.\nMasalan: <code>400000</code>",
                         reply_markup=cancel_kb())


@router.message(CourseCreate.price, F.text)
async def get_price(message: Message, state: FSMContext):
    price = parse_price(message.text)
    if price is None:
        await message.answer("Narxni raqam bilan yozing (10 000 dan 100 000 000 gacha). Masalan: <code>400000</code>")
        return
    await state.update_data(price=price)
    await state.set_state(CourseCreate.certificate)
    await message.answer(f"Narx: <b>{money(price)}</b>\n\n5/6. Fan bo'yicha <b>sertifikat rasmini</b> yuboring (agar bo'lsa):",
                         reply_markup=skip_cert_kb())


@router.message(CourseCreate.certificate, F.photo)
async def get_certificate(message: Message, state: FSMContext):
    await state.update_data(certificate=message.photo[-1].file_id)
    await _show_day_picker(message, state, edit=False)


@router.callback_query(CourseCreate.certificate, FlowCB.filter(F.action == "skipcert"))
async def skip_certificate(cb: CallbackQuery, state: FSMContext):
    await state.update_data(certificate=None)
    await cb.message.edit_text("5/6. Sertifikat: yo'q")
    await _show_day_picker(cb.message, state, edit=False)
    await cb.answer()


@router.message(CourseCreate.certificate)
async def certificate_invalid(message: Message):
    await message.answer("Sertifikatni rasm sifatida yuboring yoki «Sertifikatim yo'q» tugmasini bosing.")


# ---------- 6: dars jadvali ----------
@router.callback_query(CourseCreate.day, DayCB.filter())
async def pick_day(cb: CallbackQuery, callback_data: DayCB, state: FSMContext):
    data = await state.get_data()
    if callback_data.day in {s["weekday"] for s in data.get("slots", [])}:
        await cb.answer("Bu kun allaqachon qo'shilgan", show_alert=True)
        return
    await state.update_data(day=callback_data.day)
    await state.set_state(CourseCreate.start)
    await cb.message.edit_text(
        f"<b>{_day(callback_data.day)}</b> kuni dars soat nechada <b>boshlanadi</b>?\nMasalan: <code>14:00</code>",
        reply_markup=cancel_kb(),
    )
    await cb.answer()


@router.message(CourseCreate.start, F.text)
async def get_start(message: Message, state: FSMContext):
    start = parse_time(message.text)
    if start is None:
        await message.answer("Vaqtni to'g'ri kiriting. Masalan: <code>14:00</code>")
        return
    await state.update_data(start=start)
    await state.set_state(CourseCreate.end)
    await message.answer(f"Boshlanishi: <b>{start}</b>\nDars soat nechada <b>tugaydi</b>? Masalan: <code>17:00</code>",
                         reply_markup=cancel_kb())


@router.message(CourseCreate.end, F.text)
async def get_end(message: Message, state: FSMContext, api: ApiClient):
    data = await state.get_data()
    day, start = data["day"], data["start"]
    end = parse_time(message.text)
    if end is None or end <= start:
        await message.answer(f"Tugash vaqti to'g'ri va {start} dan keyin bo'lishi kerak. Masalan: <code>17:00</code>")
        return

    conflict = await courses_api.check_slot(api, day, start, end)
    if conflict:
        await message.answer(
            f"⚠️ <b>Bu vaqt band!</b>\n\n"
            f"{_day(day)} kuni {conflict['startTime']}–{conflict['endTime']} da "
            f"«{escape(conflict['title'])}» kursi o'tadi. Xona bitta bo'lgani uchun bir vaqtda "
            f"ikkita dars o'tkazib bo'lmaydi.\n\n"
            f"Avval dars jadvali bilan tanishib chiqishni maslahat beramiz, yoki boshqa vaqt kiriting.",
            reply_markup=conflict_kb(),
        )
        return  # holat `end` da qoladi: yangi tugash vaqtini yozsa, qayta tekshiriladi

    slots = data.get("slots", []) + [{"weekday": day, "startTime": start, "endTime": end}]
    await state.update_data(slots=slots)
    await state.set_state(CourseCreate.schedule_menu)
    await message.answer(_draft_text(slots), reply_markup=schedule_actions_kb(can_add=len(slots) < 7))


@router.callback_query(CourseCreate.end, FlowCB.filter(F.action == "retry"))
async def retry_slot(cb: CallbackQuery, state: FSMContext):
    await _show_day_picker(cb.message, state, edit=False)
    await cb.answer()


@router.callback_query(CourseCreate.schedule_menu, FlowCB.filter(F.action == "addday"))
async def add_day(cb: CallbackQuery, state: FSMContext):
    await _show_day_picker(cb.message, state, edit=True)
    await cb.answer()


@router.callback_query(CourseCreate.schedule_menu, FlowCB.filter(F.action == "save"))
async def save_course(cb: CallbackQuery, state: FSMContext, api: ApiClient):
    data = await state.get_data()
    payload = {
        "title": data["title"],
        "description": data["description"],
        "price": data["price"],
        "photo": data.get("photo"),
        "certificate": data.get("certificate"),
        "schedules": data["slots"],
    }
    try:
        await courses_api.create_course(api, cb.from_user.id, payload)
    except ApiError as e:
        if e.status == 409:  # tekshiruv bilan saqlash orasida boshqa o'qituvchi vaqtni band qilgan
            await state.update_data(slots=[])
            await cb.message.answer("⚠️ Tanlangan vaqtlardan biri shu orada band qilindi. Jadvalni qaytadan kiriting.")
            await _show_day_picker(cb.message, state, edit=False)
            await cb.answer()
            return
        text = e.message if 400 <= e.status < 500 else "Xatolik yuz berdi, keyinroq urinib ko'ring."
        await cb.answer(text, show_alert=True)
        return

    await state.clear()
    await cb.message.edit_text(f"🎉 <b>«{escape(data['title'])}»</b> kursi yaratildi!")
    await cb.message.answer("Kurslaringizni «👤 Mening» bo'limida ko'rishingiz mumkin.", reply_markup=teacher_my_menu())
    await cb.answer()


@router.message(StateFilter(CourseCreate.day, CourseCreate.schedule_menu))
async def use_buttons(message: Message):
    await message.answer("Iltimos, yuqoridagi tugmalardan foydalaning.")