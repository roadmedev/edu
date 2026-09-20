# handlers/teacher/courses.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from services.teacher_service import (
    create_course,
    get_my_courses,
    get_course_schedules,
    add_schedule,
)
from telegram.keyboards.teachers_kb import (
    get_course_detail_keyboard,
    get_courses_list_keyboard,
)
from states.teacher_course import AddCourse
from utils.filters import IsTeacher

router = Router()
router.message.filter(IsTeacher())
router.callback_query.filter(IsTeacher())


@router.callback_query(F.data == "course_add")
async def start_add_course(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddCourse.waiting_for_photo)
    await callback.message.answer(
        "📷 Kurs rasmini yuboring (URL yoki Telegram rasm):\n\n"
        "Rasm yo'q bo'lsa, \"-\" deb yozing."
    )
    await callback.answer()


@router.message(AddCourse.waiting_for_photo, F.photo)
async def add_course_photo_telegram(message: Message, state: FSMContext) -> None:
    """Telegram'dan yuklangan rasm"""
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_url=photo_id)
    await state.set_state(AddCourse.waiting_for_title)
    await message.answer("📚 Kurs nomini kiriting:")


@router.message(AddCourse.waiting_for_photo, F.text)
async def add_course_photo_url(message: Message, state: FSMContext) -> None:
    """URL yoki '-'"""
    photo_url = None if message.text == "-" else message.text
    await state.update_data(photo_url=photo_url)
    await state.set_state(AddCourse.waiting_for_title)
    await message.answer("📚 Kurs nomini kiriting:")


@router.message(AddCourse.waiting_for_title)
async def add_course_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(AddCourse.waiting_for_description)
    await message.answer("📝 Kurs tavsifini kiriting:")


@router.message(AddCourse.waiting_for_description)
async def add_course_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(AddCourse.waiting_for_price)
    await message.answer("💵 Kurs narxini kiriting (faqat son):")


@router.message(AddCourse.waiting_for_price)
async def add_course_price(message: Message, state: FSMContext) -> None:
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("⚠️ Faqat son kiriting (masalan: 350000):")
        return

    data = await state.update_data(price=price)
    await state.clear()

    # Kurs yaratish
    result = await create_course({
        "telegram_id": message.from_user.id,
        "title": data["title"],
        "description": data["description"],
        "price": price,
    })

    if "error" in result:
        await message.answer("⚠️ Xatolik yuz berdi.")
        return

    course = result["course"]
    await message.answer(
        f"✅ <b>{course['title']}</b> kursi yaratildi!\n\n"
        f"Endi dars jadvalini qo'shing:",
        parse_mode="HTML",
        reply_markup=get_course_detail_keyboard(course["id"]),
    )


# ============ KURSNI KO'RISH ============
@router.callback_query(F.data.startswith("my_course:"))
async def show_course_detail(callback: CallbackQuery) -> None:
    course_id = int(callback.data.split(":")[1])

    # Kursni topish
    courses = await get_my_courses(callback.from_user.id)
    course = next((c for c in courses if c["id"] == course_id), None)

    if not course:
        await callback.answer("Kurs topilmadi", show_alert=True)
        return

    # Jadval
    schedules = await get_course_schedules(course_id)

    schedule_text = "\n".join(
        f"  • {['', 'Dush', 'Sesh', 'Chor', 'Pay', 'Jum', 'Shan', 'Yak'][s['day_of_week']]} "
        f"{s['start_time']}-{s['end_time']}"
        for s in schedules
    ) or "  Jadval qo'shilmagan"

    text = (
        f"📚 <b>{course['title']}</b>\n\n"
        f"📝 {course.get('description') or '—'}\n\n"
        f"💵 Narx: {course.get('price', 0)} so'm\n"
        f"👥 O'quvchilar: {course.get('students_count', 0)} ta\n\n"
        f"🕐 <b>Dars jadvali:</b>\n{schedule_text}"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_course_detail_keyboard(course_id),
    )
    await callback.answer()


# ============ O'CHIRISH ============
@router.callback_query(F.data.startswith("course_delete:"))
async def confirm_delete_course(callback: CallbackQuery) -> None:
    course_id = int(callback.data.split(":")[1])
    await callback.message.answer(
        "🗑 Rostdan ham bu kursni o'chirmoqchimisiz?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Ha",
                        callback_data=f"course_delete_confirm:{course_id}",
                    ),
                    InlineKeyboardButton(text="❌ Bekor", callback_data="cancel"),
                ]
            ]
        ),
    )
    await callback.answer()