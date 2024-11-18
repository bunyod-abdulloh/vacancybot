from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline.admin_ikb import second_check_ikb
from bot.states.admin_states import AdminCheck
from data.config import CHANNEL
from loader import bot, db

router = Router()

chapters = {
    "need_partner": ["Sherik kerak", "#sherik_kerak", "Sherik"], "need_job": ["Ish joyi kerak", "#ish_kerak", "Xodim"],
    "need_worker": ["Xodim kerak", "#xodim_kerak"], "need_teacher": ["Ustoz kerak", "#ustoz_kerak", "Shogird"],
    "need_apprentice": ["Shogird kerak", "#shogird_kerak", "Ustoz"], "idoralar": "idoralar"
}


# Utility function to parse callback data
def split_data(data):
    parts = data.split(":")
    return int(parts[1]), parts[2], parts[3] if len(parts) > 3 else (None, None, None)


# Send message to user and confirm in chat
async def send_and_alert(user_id, text, call):
    try:
        await bot.send_message(chat_id=user_id, text=text)
        user_data = await bot.get_chat(user_id)
        await call.message.edit_text(f"Habar {user_data.full_name} (@{user_data.username}) ga yuborildi!")
    except Exception as e:
        await call.message.edit_text(f"Failed to send message to {user_id}: {e}")


# Generate summary message for various user types
async def generate_summary(user_data, techs, data_type, additional_info):
    techs_str = ", ".join(techs)
    techs_tags = " ".join(f"#{tech}" for tech in techs)

    if data_type == "need_worker":
        summary_templates = {
            "need_worker": (
                f"<b>{chapters[data_type][0]}</b>\n\n"
                f"🏢 <b>Idora:</b> {additional_info['idora_nomi']}\n"
                f"🧑‍💻 <b>Texnologiya:</b> {techs_str}\n"
                f"🔗 <b>Telegram:</b> {user_data['username']}\n"
                f"📞 <b>Aloqa:</b> {user_data['phone']}\n"
                f"🌎 <b>Hudud:</b> {additional_info['region']}\n"
                f"✍️ <b>Mas'ul:</b> {additional_info['masul']}\n"
                f"⌚️ <b>Murojaat qilish vaqti:</b> {additional_info['m_vaqti']}\n"
                f"🕰 <b>Ish vaqti:</b> {additional_info['i_vaqti']}\n"
                f"💰 <b>Maosh:</b> {additional_info['maosh']}\n"
                f"‼️ <b>Qo'shimcha ma'lumotlar:</b> {additional_info['qoshimcha']}\n\n"
                f"{chapters[data_type][1]} {techs_tags} #{additional_info['region_tag']}"
            )}
    else:
        if data_type in ['need_job', 'need_teacher', 'need_apprentice']:
            summary = (f"<b>{chapters[data_type][0]}</b>\n\n"
                       f"👨‍💼 <b>{chapters[data_type][2]}:</b> {user_data['full_name']}\n"
                       f"🕑 <b>Yosh:</b> {user_data['age']}\n"
                       f"🧑‍💻 <b>Texnologiya:</b> {techs_str}\n"
                       f"🔗 <b>Telegram:</b> {user_data['username']}\n"
                       f"📞 <b>Aloqa:</b> {user_data['phone']}\n"
                       f"🌎 <b>Hudud:</b> {additional_info['region']}\n"
                       f"💰 <b>Narx:</b> {additional_info['cost']}\n"
                       f"💻 <b>Kasbi:</b> {additional_info['profession']}\n"
                       f"⌚️ <b>Murojaat qilish vaqti:</b> {additional_info['apply_time']}\n"
                       f"📌 <b>Maqsad:</b> {additional_info['maqsad']}\n\n"
                       f"{chapters[data_type][1]} {techs_tags}  #{additional_info['region_tag']}")
        else:
            summary = (f"<b>{chapters[data_type][0]}</b>\n\n"
                       f"👨‍💼 <b>{chapters[data_type][2]}:</b> {user_data['full_name']}\n"
                       f"🧑‍💻 <b>Texnologiya:</b> {techs_str}\n"
                       f"🔗 <b>Telegram:</b> {user_data['username']}\n"
                       f"📞 <b>Aloqa:</b> {user_data['phone']}\n"
                       f"🌎 <b>Hudud:</b> {additional_info['region']}\n"
                       f"💰 <b>Narx:</b> {additional_info['cost']}\n"
                       f"💻 <b>Kasbi:</b> {additional_info['profession']}\n"
                       f"⌚️ <b>Murojaat qilish vaqti:</b> {additional_info['apply_time']}\n"
                       f"📌 <b>Maqsad:</b> {additional_info['maqsad']}\n\n"
                       f"{chapters[data_type][1]} {techs_tags}  #{additional_info['region_tag']}")
        summary_templates = {data_type: summary}
    return summary_templates.get(data_type, "No summary template found")


# Fetch and send user information to channel
async def get_send_user_info(user_id, data_type, row_id):
    user_data = await db.get_user_data(user_id)
    row_id = int(row_id)

    if data_type == "need_worker":
        nw_data = await db.get_idora(row_id)

        technologies = await db.get_techs(row_id, data_type)
        techs = [(await db.get_entry("technologies", "id", tech['id']))['technology_name'] for tech in technologies]
        region = (await db.get_entry("regions", "id", nw_data['region_id']))['region_name']
        additional_info = {
            "idora_nomi": nw_data['idora_nomi'],
            "masul": nw_data['masul'],
            "region": region,
            "m_vaqti": nw_data['m_vaqti'],
            "i_vaqti": nw_data['i_vaqti'],
            "maosh": nw_data['maosh'],
            "qoshimcha": nw_data['qoshimcha'],
            "region_tag": region.split(",")[0].split(" ")[0]
        }
    else:
        technologies = await db.get_techs(row_id, data_type)
        techs = [(await db.get_entry("technologies", "id", tech['id']))['technology_name'] for tech in technologies]
        job = await db.get_entry(data_type, "id", row_id)
        region = (await db.get_entry("regions", "id", job['region_id']))['region_name']
        profession = (await db.get_entry("professions", "id", job['profession_id']))['profession']
        additional_info = {
            "region": region,
            "cost": job['cost'],
            "profession": profession,
            "apply_time": job['apply_time'],
            "maqsad": job['maqsad'],
            "region_tag": region.split(",")[0].split(" ")[0]
        }
    summary = await generate_summary(user_data, techs, data_type, additional_info)
    await bot.send_message(CHANNEL, summary)


# Delete all user-related data
async def delete_user_data(telegram_id, call, department, row_id: int):
    try:
        if department == "need_worker":
            await db.delete_from_table("user_techs", "user_id", row_id)
            idora_id = (await db.get_entry(department, "id", row_id))['idora_id']
            await db.delete_from_table("idoralar", "id", idora_id)
            await db.delete_from_table(department, "id", row_id)
        else:
            user_id = (await db.get_entry("users", "telegram_id", telegram_id))['id']
            await db.delete_from_table("user_techs", "user_id", user_id)
            await db.delete_from_table(department, "user_id", user_id)
    except Exception as err:
        await call.message.edit_text(f"Error: {err}")


# Handle admin approval of request
@router.callback_query(F.data.startswith('adm_yes:'))
async def admincheck_approve(call: types.CallbackQuery):
    user_telegram, row_id, department = split_data(call.data)

    if department in chapters:
        text = f"Sizning {chapters[department][0]} bo'limi uchun yuborgan {user_telegram}{row_id} raqamli so'rovingiz qabul qilindi!"
        await get_send_user_info(user_telegram, department, row_id)
        await send_and_alert(user_telegram, text, call)


# Prompt for rejection reason
@router.callback_query(F.data.startswith("adm_no:"))
async def admincheck_reject_reason(call: types.CallbackQuery, state: FSMContext):
    user_id, row_id, department = split_data(call.data)
    await call.message.edit_text("Rad etilish sababini kiriting")
    await state.update_data(ck_telegram=user_id, ck_row=row_id, ck_department=department)
    await state.set_state(AdminCheck.partner_no)


# Confirm rejection reason
@router.message(AdminCheck.partner_no)
async def admincheck_confirm_reject(message: types.Message, state: FSMContext):
    await state.update_data(ck_text=message.text)
    data = await state.get_data()
    await message.answer("Kiritgan habaringizni tasdiqlaysizmi?", reply_markup=second_check_ikb(
        data['ck_telegram'], data['ck_row'], data['ck_department']))
    await state.set_state(AdminCheck.partner_no_)


# Finalize rejection
@router.callback_query(AdminCheck.partner_no_)
async def admincheck_finalize_reject(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    rejection_message = (
        f"Sizning <b>{chapters[data['ck_department'][0]]}</b> bo'limi uchun yuborgan {data['ck_telegram']}{data['ck_row']} "
        f"raqamli so'rovingiz rad etildi!\n\nSabab: {data['ck_text']}")
    await send_and_alert(data['ck_telegram'], rejection_message, call)
    await delete_user_data(data['ck_telegram'], call, data['ck_department'], int(data['ck_row']))
    await state.clear()
