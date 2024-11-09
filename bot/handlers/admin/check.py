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


# Send message and alert
async def send_and_alert(user_id, text, call):
    try:
        await bot.send_message(chat_id=user_id, text=text)
        user_data = await bot.get_chat(user_id)
        await call.message.edit_text(f"Habar foydalanuvchi {user_data.full_name} (@{user_data.username}) ga yuborildi!")
    except Exception as e:
        await call.message.edit_text(f"Failed to send message to {user_id}: {e}")


# Helper function to get user info
async def get_user_info(user_id, is_partner=False, is_job=False):
    user = await db.get_entry(table="users", field="telegram_id", value=user_id)
    user_datas = await db.get_entry(table="users_data", field="user_id", value=user['id'])
    get_user = None
    if is_job:
        get_user = await db.get_entry(table="srch_job", field="user_id", value=user['id'])
    if is_partner:
        get_user = await db.get_srch_partner(user_id=user['id'])
    get_profession = await db.get_entry(table="professions", field="id", value=get_user['profession_id'])
    get_region = await db.get_entry(table="regions", field="id", value=user['region_id'])
    return user, user_datas, get_user, get_profession, get_region


# Handle technologies extraction
async def get_technologies(user_id):
    technologies = await db.get_technologies(user_id=user_id)
    tech_list = []
    for tech in technologies:
        technology = await db.get_entry(table="technologies", field="id", value=tech['technology_id'])
        tech_list.append(technology['technology_name'])

    tech_str = ", ".join(tech_list)
    tech_tags = " ".join(f"#{tech.lower()}" for tech in tech_list)
    return tech_str, tech_tags


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

        await db.delete_from_table("partner_technologies", "user_id", user_id)
        await db.delete_from_table("srch_partner", "user_id", user_id)
        await db.delete_user(telegram_id=user_id)
    except Exception as err:
        await call.message.edit_text(f"Error: {err}")


# Handle admin approval of partner request
@router.callback_query(F.data.startswith('admincheck_yes:'))
async def admincheck_partner(call: types.CallbackQuery):
    user_telegram, row_id, department = split_data(call.data)
    text = f"Sizning {department} bo'limi uchun yuborgan {user_telegram}{row_id} raqamli so'rovingiz qabul qilindi!"

    if department == "Sherik kerak":
        user, user_datas, get_partner, get_profession, get_region = await get_user_info(user_telegram, is_partner=True)
        technologies, technologies_bottom = await get_technologies(user['id'])
        region = get_region['region_name'].split(',')[0].split(' ')[0]

        post = (f"{department.capitalize()}\n\n"
                f"👤 <b>Sherik:</b> {user_datas['full_name']}\n"
                f"🧑‍💻 <b>Texnologiya:</b> {technologies}\n"
                f"🔗 <b>Telegram:</b> {user_datas['username']}\n"
                f"📞 <b>Aloqa:</b> {user_datas['phone']}\n"
                f"🌎 <b>Hudud:</b> {region}\n"
                f"💰 <b>Narx:</b> {get_partner['cost']}\n"
                f"💻 <b>Kasbi:</b> {get_profession['profession_name']}\n"
                f"⌚️ <b>Murojaat qilish vaqti:</b> {get_partner['apply_time']}\n"
                f"📌 <b>Maqsad:</b> {get_partner['maqsad']}\n\n"
                f"#sherik {technologies_bottom} #{region}")
        await bot.send_message(chat_id=CHANNEL, text=post)

    await send_and_alert(user_telegram, text, call)


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

    rejection_message = (f"Sizning <b>Sherik kerak</b> bo'limi uchun yuborgan {user_id}{row_id} raqamli "
                         f"so'rovingiz rad etildi!\n\nSabab: {reason}")
    await send_and_alert(user_id, rejection_message, call)
    await delete_user_data(user_id, call)
    await state.clear()
