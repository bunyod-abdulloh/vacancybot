from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.states.admin_states import AdminCheck
from loader import bot

router = Router()


@router.callback_query(F.data.startswith('admincheck_yes:'))
async def admincheck_partner(call: types.CallbackQuery):
    user_id = call.data.split(':')[1]
    row_id = call.data.split(':')[2]
    await bot.send_message(
        chat_id=user_id,
        text=f"Sizning <b>Sherik kerak</b> bo'limi uchun yuborgan {user_id}{row_id} raqamli so'rovingiz qabul qilindi!"
    )
    await call.message.edit_text(
        text="Habar foydalanuvchiga yuborildi!"
    )


@router.callback_query(F.data.startswith("admincheck_no:"))
async def admincheck_no_rtr(call: types.CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]
    row_id = call.data.split(":")[2]
    await call.message.edit_text(
        text="Rad etilish sababini kiriting"
    )
    await state.update_data(
        user_id=user_id,
        row_id=row_id
    )
    await state.set_state(
        AdminCheck.partner_no
    )


@router.message(AdminCheck.partner_no)
async def admincheck_no_partner(message: types.Message, state: FSMContext):
    await state.update_data(
        no_text_partner=message.text
    )
    await message.answer(
        text="Kiritgan habaringizni tasdiqlaysizmi?"
    )
    await state.set_state(AdminCheck.partner_no_)
