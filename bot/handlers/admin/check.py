from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline.admin_ikb import second_check_ikb
from bot.states.admin_states import AdminCheck
from data.config import CHANNEL
from loader import bot, db

router = Router()


# Utility function to split callback data
def split_data(data):
    parts = data.split(":")
    return int(parts[1]), parts[2], parts[3] if len(parts) > 3 else (None, None, None)


# Send message to user
async def send_message_(user_id, text, call):
    try:
        await bot.send_message(chat_id=user_id, text=text)
    except Exception as e:
        await call.message.edit_text(text=f"Failed to send message to {user_id}: {e}")


async def alert_message_check(user_id, call):
    user_data = await bot.get_chat(user_id)
    await call.message.edit_text(f"Habar foydalanuvchi {user_data.full_name} (@{user_data.username}) ga yuborildi!")


# Delete user-related data from the database
async def delete_user_data(user_id, call):
    try:
        user = await db.get_entry(table="users", field="telegram_id", value=user_id)
        if not user:
            return

        srch_partner = await db.get_entry(table="srch_partner", field="user_id", value=user['id'])
        if srch_partner:
            await db.delete_from_table("regions", "id", srch_partner['region_id'])
            await db.delete_from_table("professions", "id", srch_partner['profession_id'])

        partner_technologies = await db.get_technologies(user_id=user_id)
        for tech in partner_technologies:
            await db.delete_from_table("technologies", "id", tech['technology_id'])

        await db.delete_from_table("partner_technologies", "user_id", user_id)
        await db.delete_from_table("srch_partner", "user_id", user_id)
        await db.delete_user(telegram_id=user_id)
    except Exception as err:
        await call.message.edit_text(text=f"Error: {err}")


# Handle admin approval of partner request
@router.callback_query(F.data.startswith('admincheck_yes:'))
async def admincheck_partner(call: types.CallbackQuery):
    user_telegram, row_id, department = split_data(call.data)
    text = f"Sizning {department} bo'limi uchun yuborgan {user_telegram}{row_id} raqamli so'rovingiz qabul qilindi!"
    try:
        user = await db.get_entry(table="users", field="telegram_id", value=user_telegram)
        technologies = str()
        technologies_bottom = str()
        get_technology = await db.get_technologies(user_id=user['id'])
        if len(get_technology) == 1:
            technologies = get_technology[0]['technology_name']
            technologies_bottom = f"#{get_technology[0]['technology_name']}"
        else:
            for technology in get_technology:
                get_technology_ = await db.get_entry(table="technologies", field="technology_id",
                                                     value=technology['id'])
                technologies += f"{get_technology_['technology_name']}, "
                technologies_bottom += f"#{get_technology_['technology_name'].lower()} "
        get_region = await db.get_entry(table="regions", field="id", value=user['region_id'])
        region = get_region['region_name'].split(",")[0] if "," in get_region['region_name'] else \
            get_region['region_name'].split(" ")[0]

        get_partner = await db.get_entry(table="srch_partner", field="user_id", value=user['id'])
        get_profession = await db.get_entry(table="professions", field="id", value=get_partner['profession_id'])

        if department == "Sherik kerak":
            post = (f"{department.capitalize()}"
                    f"👤 < b > Sherik: < / b > {user['full_name']}\n"
                    f"🧑‍💻 <b>Texnologiya:</b> {technologies}\n"
                    f"🔗 <b>Telegram:</b> {user['username']}\n"
                    f"📞 <b>Aloqa</b> {user['phone']}\n"
                    f"🌎 <b>Hudud:</b> {region}\n"
                    f"💰 <b>Narx:</b> {get_partner['cost']}\n"
                    f"💻 <b>Kasbi:</b> {get_profession['profession_name']}\n"
                    f"⌚️ <b>Murojaat qilish vaqti:</b> {get_partner['apply_time']}\n"
                    f"📌 <b>Maqsad:</b> {get_partner['maqsad']}\n\n"
                    f"#sherik {technologies_bottom} #{region}")
            await bot.send_message(chat_id=CHANNEL, text=post)
        await send_message_(user_telegram, text, call)
        await alert_message_check(user_telegram, call)

    except Exception as err:
        await call.message.edit_text(f"Error: {err}")


# Handle admin rejection of partner request (step 1: ask for reason)
@router.callback_query(F.data.startswith("admincheck_no:"))
async def admincheck_no_rtr(call: types.CallbackQuery, state: FSMContext):
    user_id, row_id, department = split_data(call.data)
    await call.message.edit_text("Rad etilish sababini kiriting")
    await state.update_data(pr_user_id=user_id, pr_row_id=row_id, department=department)
    await state.set_state(AdminCheck.partner_no)


# Handle admin rejection of partner request (step 2: confirm reason)
@router.message(AdminCheck.partner_no)
async def admincheck_no_partner(message: types.Message, state: FSMContext):
    await state.update_data(pr_no_text=message.text)
    data = await state.get_data()

    user_id, row_id, department = data['pr_user_id'], data['pr_row_id'], data['department']
    await message.answer("Kiritgan habaringizni tasdiqlaysizmi?", reply_markup=second_check_ikb(
        user_id, row_id, department))
    await state.set_state(AdminCheck.partner_no_)


# Final step after confirming rejection reason
@router.callback_query(AdminCheck.partner_no_)
async def admincheck_no_partner_rtr(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    user_id, row_id, department = int(data['pr_user_id']), data['pr_row_id'], data['department']
    reason = data['pr_no_text']

    # Send rejection message and delete user data
    rejection_message = f"Sizning <b>Sherik kerak</b> bo'limi uchun yuborgan {user_id}{row_id} raqamli " \
                        f"so'rovingiz rad etildi!\n\nSabab: {reason}"
    await send_message_(user_id, rejection_message, call)
    await delete_user_data(user_id, call)
    await alert_message_check(user_id, call)
    await state.clear()
