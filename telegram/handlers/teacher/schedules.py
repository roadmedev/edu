# handlers/teacher/schedules.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from services.teacher_service import add_schedule, get_course_schedules
from keyboards.schedule_kb import (
    get_days_keyboard,
    get_schedule_actions_keyboard,
)
from states.teacher_schedule import AddSchedule
from utils.filters import IsTeacher

router = Router()
router.message.filter(IsTeacher())
router.callback_query.filter(IsTeacher())


@router.callback_query(F.data.startswith("schedule_add:"))
async def start_add_schedule(callback: CallbackQuery, state: FSMContext) -> None:
    course_id = int(callback.data.split(":")[1])
    await state.update_data(course_id=course_id)
    await state.set_state(AddSchedule.waiting_for_day)
    await callback.message.answer(
        "📅 Haftaning kunini tanlang:",
        reply_markup=get_days_keyboard(course_id),
    )
    await callback.answer()


@router.callback_query(AddSchedule.waiting_for_day, F.data.startswith("sched_day:"))
async def choose_day(callback: CallbackQuery, state: FSMContext) -> None:
    _, course_id, day = callback.data.split(":")
    await state.update_data(day_of_week=int(day))
    await state.set_state(AddSchedule.waiting_for_start)
    await callback.message.answer(
        "🕐 Boshlanish vaqtini kiriting (masalan: 09:00):"
    )
    await callback.answer()


@router.message(AddSchedule.waiting_for_start)
async def set_start_time(message: Message, state: FSMContext) -> None:
    # Vaqt formatini tekshirish
    time_str = message.text.strip()
    if not _is_valid_time(time_str):
        await message.answer("⚠️ Noto'g'ri format. Masalan: 09:00")
        return

    await state.update_data(start_time=time_str)
    await state.set_state(AddSchedule.waiting_for_end)
    await message.answer("🕐 Tugash vaqtini kiriting (masalan: 11:00):")


@router.message(AddSchedule.waiting_for_end)
async def set_end_time(message: Message, state: FSMContext) -> None:
    time_str = message.text.strip()
    if not _is_valid_time(time_str):
        await message.answer("⚠️ Noto'g'ri format. Masalan: 11:00")
        return

    data = await state.update_data(end_time=time_str)

    # Conflict check
    result = await add_schedule({
        "course_id": data["course_id"],
        "day_of_week": data["day_of_week"],
        "start_time": data["start_time"],
        "end_time": data["end_time"],
    })

    if "error" in result:
        # Conflict bo'lsa
        conflicts = result.get("conflicts", [])
        if conflicts:
            conflict_text = "\n".join([f"• {c['title']}" for c in conflicts])
            await message.answer(
                f"⚠️ <b>Bu vaqtda boshqa kurs mavjud:</b>\n\n{conflict_text}\n\n"
                f"Boshqa vaqtni kiriting yoki dars jadvalini tekshiring.",
                parse_mode="HTML",
            )
        else:
            await message.answer(f"⚠️ Xatolik: {result['error']}")
        return

    await state.set_state(AddSchedule.waiting_for_more)
    await message.answer(
        "✅ Jadval qo'shildi!\n\n"
        "Yana kun qo'shasizmi?",
        reply_markup=get_schedule_actions_keyboard(data["course_id"]),
    )


@router.callback_query(AddSchedule.waiting_for_more, F.data.startswith("sched_more:"))
async def add_more_schedule(callback: CallbackQuery, state: FSMContext) -> None:
    course_id = int(callback.data.split(":")[1])
    await state.set_state(AddSchedule.waiting_for_day)
    await callback.message.answer(
        "📅 Yana kunni tanlang:",
        reply_markup=get_days_keyboard(course_id),
    )
    await callback.answer()


@router.callback_query(F.data == "sched_done")
async def finish_schedule(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("✅ Dars jadvali saqlandi!")
    await callback.answer()


def _is_valid_time(time_str: str) -> bool:
    """09:00 formatini tekshirish"""
    try:
        h, m = time_str.split(":")
        return 0 <= int(h) <= 23 and 0 <= int(m) <= 59
    except (ValueError, AttributeError):
        return False