from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline.admin_ikb import partner_check_ikb
from bot.states.admin_states import AdminCheck
from loader import bot, db

router = Router()


# Utility function to split callback data
def split_data(data):
    parts = data.split(":")
    return (parts[1], parts[2]) if len(parts) > 2 else (None, None)


# Send message to user
async def send_message(user_id, text):
    try:
        await bot.send_message(chat_id=user_id, text=text)
    except Exception as e:
        print(f"Failed to send message to {user_id}: {e}")


# Delete user-related data from the database
async def delete_user_data(user_id):
    try:
        user = await db.get_entry(table="users", field="telegram_id", value=user_id)
        if not user:
            return

        srch_partner = await db.get_entry(table="srch_partner", field="user_id", value=user['id'])
        if srch_partner:
            await db.delete_from_table("regions", "id", srch_partner['region_id'])
            await db.delete_from_table("professions", "id", srch_partner['profession_id'])

        partner_technologies = await db.get_partner_technologies(user_id=user_id)
        for tech in partner_technologies:
            await db.delete_from_table("technologies", "id", tech['technology_id'])

        await db.delete_from_table("partner_technologies", "user_id", user_id)
        await db.delete_from_table("srch_partner", "user_id", user_id)
        await db.delete_user(telegram_id=user_id)
    except Exception as e:
        print(f"Failed to delete user data for {user_id}: {e}")


# Handle admin approval of partner request
@router.callback_query(F.data.startswith('admincheck_yes:'))
async def admincheck_partner(call: types.CallbackQuery):
    user_id, row_id = split_data(call.data)
    text = f"Sizning Sherik kerak bo'limi uchun yuborgan {user_id}{row_id} raqamli so'rovingiz qabul qilindi!"
    await send_message(user_id, text)
    await call.message.edit_text("Habar foydalanuvchiga yuborildi!")


# Handle admin rejection of partner request (step 1: ask for reason)
@router.callback_query(F.data.startswith("admincheck_no:"))
async def admincheck_no_rtr(call: types.CallbackQuery, state: FSMContext):
    user_id, row_id = split_data(call.data)
    await call.message.edit_text("Rad etilish sababini kiriting")
    await state.update_data(pr_user_id=user_id, pr_row_id=row_id)
    await state.set_state(AdminCheck.partner_no)


# Handle admin rejection of partner request (step 2: confirm reason)
@router.message(AdminCheck.partner_no)
async def admincheck_no_partner(message: types.Message, state: FSMContext):
    await state.update_data(pr_no_text=message.text)
    data = await state.get_data()

    user_id, row_id = data['pr_user_id'], data['pr_row_id']
    await message.answer("Kiritgan habaringizni tasdiqlaysizmi?", reply_markup=partner_check_ikb(user_id, row_id))
    await state.set_state(AdminCheck.partner_no_)


# Final step after confirming rejection reason
@router.callback_query(AdminCheck.partner_no_)
async def admincheck_no_partner_rtr(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    user_id, row_id = int(data['pr_user_id']), data['pr_row_id']
    reason = data['pr_no_text']

    await send_message(user_id,
                       f"Sizning <b>Sherik kerak</b> bo'limi uchun yuborgan {user_id}{row_id} raqamli so'rovingiz rad etildi!\n\nSabab: {reason}")
    await delete_user_data(user_id)
    await call.message.edit_text("Habar foydalanuvchiga yuborildi!")
    await state.clear()
