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


# Fetch user and related information based on type
async def get_user_info(user_id, data_type=None):
    user = await db.get_entry(table="users", field="telegram_id", value=user_id)
    user_data = await db.get_entry(table="users_data", field="user_id", value=user['id'])
    extra_data = None
    if data_type == "partner":
        extra_data = await db.get_srch_partner(user_id=user['id'])
    elif data_type == "job":
        extra_data = await db.get_entry(table="srch_job", field="user_id", value=user['id'])

    profession = await db.get_entry(table="professions", field="id", value=extra_data['profession_id'])
    region = await db.get_entry(table="regions", field="id", value=user['region_id'])
    return user, user_data, extra_data, profession, region


# Extract user technologies and format tags
async def get_technologies(user_id):
    technologies = await db.get_technologies(user_id=user_id)
    tech_list = []

    for tech in technologies:
        technology = await db.get_entry(table="technologies", field="id", value=tech['technology_id'])
        tech_list.append(technology['technology_name'])

    return ", ".join(tech_list), " ".join(f"#{tech.lower()}" for tech in tech_list)


# Delete all user-related data
async def delete_user_data(user_id, call):
    try:
        user = await db.get_entry(table="users", field="telegram_id", value=user_id)
        if not user:
            return

        await db.delete_from_table("partner_technologies", "user_id", user_id)
        await db.delete_from_table("srch_partner", "user_id", user_id)
        await db.delete_user(telegram_id=user_id)
    except Exception as err:
        await call.message.edit_text(f"Error: {err}")


# Helper to generate post text based on user and data type
def format_post_text(department, user_data, extra_data, profession, region, technologies, technologies_bottom):
    region_name = region['region_name']  # region nomini olish

    return (
        f"<b>{department.capitalize()}</b>\n\n"
        f"👤 <b>{'Sherik' if department == 'Sherik kerak' else 'Xodim'}:</b> {user_data['full_name']}\n"
        f"🧑‍💻 <b>Texnologiya:</b> {technologies}\n"
        f"🔗 <b>Telegram:</b> {user_data['username']}\n"
        f"📞 <b>Aloqa:</b> {user_data['phone']}\n"
        f"🌎 <b>Hudud:</b> {region_name}\n"
        f"💰 <b>Narx:</b> {extra_data['cost']}\n"
        f"💻 <b>Kasbi:</b> {profession['profession_name']}\n"
        f"⌚️ <b>Murojaat qilish vaqti:</b> {extra_data['apply_time']}\n"
        f"📌 <b>Maqsad:</b> {extra_data['maqsad']}\n\n"
        f"#{department.lower().replace(' ', '_')} {technologies_bottom} #{region_name.split(',')[0].split(' ')[0]}"
    )


# Handle admin approval of partner or job request
@router.callback_query(F.data.startswith('admincheck_yes:'))
async def admincheck_approve(call: types.CallbackQuery):
    user_telegram, row_id, department = split_data(call.data)
    text = f"Sizning {department} bo'limi uchun yuborgan {user_telegram}{row_id} raqamli so'rovingiz qabul qilindi!"

    data_type = "partner" if department == "Sherik kerak" else "job" if department == "Ish joyi kerak" else None

    user, user_data, extra_data, profession, region = await get_user_info(user_telegram, data_type=data_type)
    technologies, technologies_bottom = await get_technologies(user['id'])

    post = format_post_text(department, user_data, extra_data, profession, region, technologies, technologies_bottom)
    await bot.send_message(chat_id=CHANNEL, text=post)
    await send_and_alert(user_telegram, text, call)


# Ask for reason when rejecting request
@router.callback_query(F.data.startswith("admincheck_no:"))
async def admincheck_reject_reason(call: types.CallbackQuery, state: FSMContext):
    user_id, row_id, department = split_data(call.data)
    await call.message.edit_text("Rad etilish sababini kiriting")
    await state.update_data(pr_user_id=user_id, pr_row_id=row_id, department=department)
    await state.set_state(AdminCheck.partner_no)


# Confirm reason for rejection
@router.message(AdminCheck.partner_no)
async def admincheck_confirm_reject(message: types.Message, state: FSMContext):
    await state.update_data(pr_no_text=message.text)
    data = await state.get_data()

    await message.answer("Kiritgan habaringizni tasdiqlaysizmi?", reply_markup=second_check_ikb(
        data['pr_user_id'], data['pr_row_id'], data['department']))
    await state.set_state(AdminCheck.partner_no_)


# Final step after confirming rejection reason
@router.callback_query(AdminCheck.partner_no_)
async def admincheck_finalize_reject(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    rejection_message = (
        f"Sizning <b>{data['department']}</b> bo'limi uchun yuborgan {data['pr_user_id']}{data['pr_row_id']} raqamli "
        f"so'rovingiz rad etildi!\n\nSabab: {data['pr_no_text']}")

    await send_and_alert(data['pr_user_id'], rejection_message, call)
    await delete_user_data(data['pr_user_id'], call)
    await state.clear()
