from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from api import admin as admin_api
from api.client import ApiClient
from callbacks.broadcast import BroadcastCB
from filters.role import RoleFilter
from keyboards.inline.broadcast import broadcast_confirm_kb
from states.broadcast import BroadcastStates

router = Router(name="admin_broadcast")
router.message.filter(RoleFilter("admin"))
router.callback_query.filter(RoleFilter("admin"))

TARGET_TITLES = {
    "users": "Oddiy foydalanuvchilar",
    "teachers": "O'qituvchilar",
    "students": "O'quvchilar",
}


@router.callback_query(BroadcastCB.filter(F.action == "start"))
async def start_broadcast(cb: CallbackQuery, callback_data: BroadcastCB, state: FSMContext):
    await state.set_state(BroadcastStates.text)
    await state.update_data(target=callback_data.target)
    await cb.message.answer(f"✍️ <b>{TARGET_TITLES[callback_data.target]}</b>ga yuboriladigan xabar matnini yozing:")
    await cb.answer()


@router.message(BroadcastStates.text, F.text)
async def receive_text(message: Message, state: FSMContext):
    await state.update_data(draft=message.text)
    await state.set_state(BroadcastStates.confirm)
    data = await state.get_data()
    await message.answer(
        f"📢 <b>Xabar matni</b> ({TARGET_TITLES[data['target']]}):\n\n{message.text}",
        reply_markup=broadcast_confirm_kb(),
    )


@router.message(BroadcastStates.text)
async def receive_text_invalid(message: Message):
    await message.answer("Iltimos, xabar matnini oddiy matn ko'rinishida yozing.")


@router.callback_query(BroadcastStates.confirm, BroadcastCB.filter(F.action == "edit"))
async def edit_broadcast(cb: CallbackQuery, state: FSMContext):
    await state.set_state(BroadcastStates.text)
    await cb.message.edit_text("✍️ Yangi xabar matnini yozing:")
    await cb.answer()


@router.callback_query(BroadcastStates.confirm, BroadcastCB.filter(F.action == "cancel"))
async def cancel_broadcast(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("❌ Bekor qilindi.")
    await cb.answer()


@router.callback_query(BroadcastStates.confirm, BroadcastCB.filter(F.action == "confirm"))
async def confirm_broadcast(cb: CallbackQuery, state: FSMContext, api: ApiClient):
    data = await state.get_data()
    target, text = data["target"], data["draft"]
    await state.clear()
    await cb.message.edit_text(f"⏳ Yuborilmoqda...\n\n{text}")
    await cb.answer()

    ids = await admin_api.broadcast_targets(api, cb.from_user.id, target)
    sent = failed = 0
    for tg_id in ids:
        try:
            await cb.bot.send_message(tg_id, text)
            sent += 1
        except TelegramAPIError:
            failed += 1

    tail = f", {failed} taga yetkazilmadi" if failed else ""
    await cb.message.edit_text(
        f"✅ <b>Xabar yuborildi</b>\n👥 {TARGET_TITLES[target]}: {sent} taga yetkazildi{tail}"
    )