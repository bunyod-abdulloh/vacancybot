from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline.admin_ikb import partner_check_ikb
from bot.states.admin_states import AdminCheck
from loader import bot, db

router = Router()


def split_data(data):
    return data.split(":")[1], data.split(":")[2]


async def send_rejection_message(user_id, row_id, reason):
    await bot.send_message(
        chat_id=user_id,
        text=f"Sizning <b>Sherik kerak</b> bo'limi uchun yuborgan {user_id}{row_id} raqamli so'rovingiz rad etildi!"
             f"\n\nSabab: {reason}"
    )


async def delete_user_data(user_id):
    user = await db.get_entry(table="users", field="telegram_id", value=user_id)
    srch_partner = await db.get_entry(table="srch_partner", field="user_id", value=user['id'])
    await db.delete_from_table(table="regions", field="id", value=srch_partner['region_id'])
    await db.delete_from_table(table="professions", field="id", value=srch_partner['profession_id'])

    partner_technologies = await db.get_partner_technologies(partner_id=user_id)
    for technology in partner_technologies:
        await db.delete_from_table(table="technologies", field="id", value=technology['technology_id'])

    await db.delete_from_table(table="partner_technologies", field="partner_id", value=user_id)
    await db.delete_from_table(table="srch_partner", field="user_id", value=user_id)
    await db.delete_user(telegram_id=user_id)


@router.callback_query(F.data.startswith('admincheck_yes:'))
async def admincheck_partner(call: types.CallbackQuery):
    user_id, row_id = split_data(call.data)
    await bot.send_message(
        chat_id=user_id,
        text=f"Sizning <b>Sherik kerak</b> bo'limi uchun yuborgan {user_id}{row_id} raqamli so'rovingiz qabul qilindi!"
    )
    await call.message.edit_text(text="Habar foydalanuvchiga yuborildi!")


@router.callback_query(F.data.startswith("admincheck_no:"))
async def admincheck_no_rtr(call: types.CallbackQuery, state: FSMContext):
    user_id, row_id = split_data(call.data)
    await call.message.edit_text(text="Rad etilish sababini kiriting")
    await state.update_data(pr_user_id=user_id, pr_row_id=row_id)
    await state.set_state(AdminCheck.partner_no)


@router.message(AdminCheck.partner_no)
async def admincheck_no_partner(message: types.Message, state: FSMContext):
    await state.update_data(pr_no_text=message.text)
    data = await state.get_data()
    user_id, row_id = data['pr_user_id'], data['pr_row_id']
    await message.answer(
        text="Kiritgan habaringizni tasdiqlaysizmi?",
        reply_markup=partner_check_ikb(user_id, row_id)
    )
    await state.set_state(AdminCheck.partner_no_)


@router.callback_query(AdminCheck.partner_no_)
async def admincheck_no_partner_rtr(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith("admincheck_no:"):
        await state.clear()
        await admincheck_no_rtr(call, state)
    else:
        data = await state.get_data()
        user_id, row_id, reason = int(data['pr_user_id']), data['pr_row_id'], data['pr_no_text']
        await send_rejection_message(user_id, row_id, reason)
        await delete_user_data(user_id)
        await call.message.edit_text(text="Habar foydalanuvchiga yuborildi!")
        await state.clear()
