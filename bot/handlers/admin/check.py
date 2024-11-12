# from aiogram import Router, F, types
# from aiogram.fsm.context import FSMContext
#
# from bot.keyboards.inline.admin_ikb import second_check_ikb
# from bot.states.admin_states import AdminCheck
# from data.config import CHANNEL
# from loader import bot, db
#
# router = Router()
#
# chapters = {"need_partner": "Sherik kerak", "need_job": "Ish joyi kerak", "need_worker": "Xodim kerak",
#             "need_teacher": "Ustoz kerak", "need_apprentice": "Shogird kerak", "idoralar": "idoralar"}
#
#
# # Utility function to split callback data
# def split_data(data):
#     parts = data.split(":")
#     return int(parts[1]), parts[2], parts[3] if len(parts) > 3 else (None, None, None)
#
#
# # Send message and alert
# async def send_and_alert(user_id, text, call):
#     try:
#         await bot.send_message(chat_id=user_id, text=text)
#         user_data = await bot.get_chat(user_id)
#         await call.message.edit_text(f"Habar foydalanuvchi {user_data.full_name} (@{user_data.username}) ga yuborildi!")
#     except Exception as e:
#         await call.message.edit_text(f"Failed to send message to {user_id}: {e}")
#
#
# # Fetch user and related information based on type
# async def get_send_user_info(user_id, data_type):
#     user = await db.get_entry(table="users", field="telegram_id", value=user_id)
#     user_data = await db.get_entry(table="users_data", field="user_id", value=user['id'])
#
#     get_technologies = await db.get_entries(table="user_techs", field="user_id", value=user['id'])
#     tech_list = []
#     techs_top = str()
#     techs_bottom = str()
#     summary = str()
#
#     if len(get_technologies) == 1:
#         techs_top += (await db.get_entry(table="technologies", field="id", value=get_technologies[0]['id']))[
#             'technology_name']
#         techs_bottom += f"#{(await db.get_entry(table='technologies', field='id', value=get_technologies[0]['id']))['technology_name']}"
#     else:
#         for tech in get_technologies:
#             technology = await db.get_entry(table="technologies", field="id", value=tech['id'])
#             tech_list.append(technology['technology_name'])
#             techs_top += f", {technology['technology_name']}"
#             techs_bottom += f"#{technology['technology_name']} "
#
#     if data_type == "need_worker":
#         get_idora = await db.get_entry(table="idoralar", field="user_id", value=user['id'])
#         get_worker = await db.get_entry(table=data_type, field="idora_id", value=get_idora['id'])
#         get_region = await db.get_entry(table="regions", field="id", value=get_idora['region_id'])
#         region = get_region['region_name'].split(",")[0].split(" ")[0]
#         summary += (f"<b>Xodim kerak</b>\n\n"
#                     f"🏢 <b>Idora:</b> {get_idora['idora_nomi']}\n"
#                     f"🧑‍💻 <b>Texnologiya:</b> {techs_top}\n"
#                     f"🔗 <b>Telegram:</b> {user_data['username']}\n"
#                     f"📞 <b>Aloqa:</b> {user_data['phone']}\n"
#                     f"🌎 <b>Hudud:</b> {get_region['region_name']}\n"
#                     f"✍️ <b>Mas'ul:</b> {get_idora['masul']}\n"
#                     f"⌚️ <b>Murojaat qilish vaqti:</b> {get_worker['m_vaqti']}\n"
#                     f"🕰 <b>Ish vaqti:</b> {get_worker['i_vaqti']}\n"
#                     f"💰 <b>Maosh:</b> {get_worker['maosh']}\n"
#                     f"‼️ <b>Qo'shimcha ma'lumotlar:</b> {get_idora['qoshimcha']}\n\n"
#                     f"#xodim_kerak {techs_bottom} #{region}")
#     else:
#         get_datas = await db.get_entry(table=data_type, field="user_id", value=user['id'])
#         get_region = await db.get_entry(table="regions", field="id", value=get_datas['region_id'])
#         region = get_region['region_name'].split(",")[0].split(" ")[0]
#
#         get_profession = await db.get_entry(table="professions", field="id", value=get_datas['profession_id'])
#
#         if data_type == "need_partner":
#             summary += (f"<b>Sherik kerak</b>\n\n"
#                         f"👤 <b>Sherik:</b> {user_data['full_name']}\n"
#                         f"🧑‍💻 <b>Texnologiya:</b> {techs_top}\n"
#                         f"🔗 <b>Telegram:</b> {user_data['username']}\n"
#                         f"📞 <b>Aloqa:</b> {user_data['phone']}\n"
#                         f"🌎 <b>Hudud:</b> {get_region['region_name']}\n"
#                         f"💰 <b>Narx:</b> {get_datas['cost']}\n"
#                         f"💻 <b>Kasbi:</b> {get_profession['profession_name']}\n"
#                         f"⌚️ <b>Murojaat qilish vaqti:</b> {get_datas['apply_time']}\n"
#                         f"📌 <b>Maqsad:</b> {get_datas['maqsad']}\n\n"
#                         f"#sherik {techs_bottom} #{region}")
#
#         if data_type == "need_job":
#             summary += (f"<b>Ish joyi kerak</b>\n\n"
#                         f"👤 <b>Xodim:</b> {user_data['full_name']}\n"
#                         f"🕑 <b>Yosh:</b> {user_data['age']}\n"
#                         f"🧑‍💻 <b>Texnologiya:</b> {techs_top}\n"
#                         f"🔗 <b>Telegram:</b> {user_data['username']}\n"
#                         f"📞 <b>Aloqa:</b> {user_data['phone']}\n"
#                         f"🌎 <b>Hudud:</b> {get_region['region_name']}\n"
#                         f"💰 <b>Narx:</b> {get_datas['cost']}\n"
#                         f"💻 <b>Kasbi:</b> {get_profession['profession_name']}\n"
#                         f"⌚️ <b>Murojaat qilish vaqti:</b> {get_datas['apply_time']}\n"
#                         f"📌 <b>Maqsad:</b> {get_datas['maqsad']}\n\n"
#                         f"#xodim {techs_bottom} #{region}")
#
#         if data_type == "need_teacher":
#             summary += (f"<b>Ustoz kerak</b>\n\n"
#                         f"👤 <b>Shogird:</b> {user_data['full_name']}\n"
#                         f"🕑 <b>Yosh:</b> {user_data['age']}\n"
#                         f"🧑‍💻 <b>Texnologiya:</b> {techs_top}\n"
#                         f"🔗 <b>Telegram:</b> {user_data['username']}\n"
#                         f"📞 <b>Aloqa:</b> {user_data['phone']}\n"
#                         f"🌎 <b>Hudud:</b> {get_region['region_name']}\n"
#                         f"💰 <b>Narx:</b> {get_datas['cost']}\n"
#                         f"💻 <b>Kasbi:</b> {get_profession['profession_name']}\n"
#                         f"⌚️ <b>Murojaat qilish vaqti:</b> {get_datas['apply_time']}\n"
#                         f"📌 <b>Maqsad:</b> {get_datas['maqsad']}\n\n"
#                         f"#ustoz_kerak {techs_bottom} #{region}")
#         if data_type == "need_apprentice":
#             summary += (f"<b>Shogird kerak</b>\n\n"
#                         f"👤 <b>Ustoz:</b> {user_data['full_name']}\n"
#                         f"🕑 <b>Yosh:</b> {user_data['age']}\n"
#                         f"🧑‍💻 <b>Texnologiya:</b> {techs_top}\n"
#                         f"🔗 <b>Telegram:</b> {user_data['username']}\n"
#                         f"📞 <b>Aloqa:</b> {user_data['phone']}\n"
#                         f"🌎 <b>Hudud:</b> {get_region['region_name']}\n"
#                         f"💰 <b>Narx:</b> {get_datas['cost']}\n"
#                         f"💻 <b>Kasbi:</b> {get_profession['profession_name']}\n"
#                         f"⌚️ <b>Murojaat qilish vaqti:</b> {get_datas['apply_time']}\n"
#                         f"📌 <b>Maqsad:</b> {get_datas['maqsad']}\n\n"
#                         f"#shogird {techs_bottom} #{region}")
#     await bot.send_message(chat_id=CHANNEL, text=summary)
#
#
# # Delete all user-related data
# async def delete_user_data(telegram_id, call, department, row_id: int):
#     try:
#         user_id = (await db.get_entry(table="users", field="telegram_id", value=telegram_id))['id']
#         if not user_id:
#             return
#         await db.delete_from_table(table="users_data", field="user_id", value=user_id)
#         if department == "need_worker":
#             idora_id = (await db.get_entry(table=department, field="id", value=row_id))['idora_id']
#             await db.delete_from_table(table="user_techs", field="user_id", value=idora_id)
#             await db.delete_from_table(table="idoralar", field="id", value=idora_id)
#             await db.delete_from_table(table=department, field="id", value=row_id)
#         else:
#             await db.delete_from_table(table="user_techs", field="user_id", value=user_id)
#             await db.delete_from_table(table=department, field="user_id", value=user_id)
#     except Exception as err:
#         await call.message.edit_text(f"Error: {err}")
#
#
# # Handle admin approval of partner or job request
# @router.callback_query(F.data.startswith('admincheck_yes:'))
# async def admincheck_approve(call: types.CallbackQuery):
#     user_telegram, row_id, department = split_data(call.data)
#
#     if department in chapters.keys():
#         text = f"Sizning {chapters[department]} bo'limi uchun yuborgan {user_telegram}{row_id} raqamli so'rovingiz qabul qilindi!"
#         await get_send_user_info(user_id=user_telegram, data_type=department)
#         await send_and_alert(user_telegram, text, call)
#
#
# # Ask for reason when rejecting request
# @router.callback_query(F.data.startswith("admincheck_no:"))
# async def admincheck_reject_reason(call: types.CallbackQuery, state: FSMContext):
#     user_id, row_id, department = split_data(call.data)
#     await call.message.edit_text("Rad etilish sababini kiriting")
#     await state.update_data(ck_telegram=user_id, ck_row=row_id, ck_department=department)
#     await state.set_state(AdminCheck.partner_no)
#
#
# # Confirm reason for rejection
# @router.message(AdminCheck.partner_no)
# async def admincheck_confirm_reject(message: types.Message, state: FSMContext):
#     await state.update_data(ck_text=message.text)
#     data = await state.get_data()
#
#     await message.answer("Kiritgan habaringizni tasdiqlaysizmi?", reply_markup=second_check_ikb(
#         data['ck_telegram'], data['ck_row'], data['ck_department']))
#     await state.set_state(AdminCheck.partner_no_)
#
#
# # Final step after confirming rejection reason
# @router.callback_query(AdminCheck.partner_no_)
# async def admincheck_finalize_reject(call: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     rejection_message = (
#         f"Sizning <b>{chapters[data['ck_department']]}</b> bo'limi uchun yuborgan {data['ck_telegram']}{data['ck_row']} raqamli "
#         f"so'rovingiz rad etildi!\n\nSabab: {data['ck_text']}")
#     await send_and_alert(data['ck_telegram'], rejection_message, call)
#     await delete_user_data(telegram_id=data['ck_telegram'], call=call, department=data['ck_department'],
#                            row_id=int(data['ck_row']))
#     await state.clear()

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline.admin_ikb import second_check_ikb
from bot.states.admin_states import AdminCheck
from data.config import CHANNEL
from loader import bot, db

router = Router()

chapters = {
    "need_partner": "Sherik kerak", "need_job": "Ish joyi kerak", "need_worker": "Xodim kerak",
    "need_teacher": "Ustoz kerak", "need_apprentice": "Shogird kerak", "idoralar": "idoralar"
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
        await call.message.edit_text(f"Habar {user_data.full_name} (@{user_data.username}) ga yubrildi!")
    except Exception as e:
        await call.message.edit_text(f"Failed to send message to {user_id}: {e}")


# Generate summary message for various user types
async def generate_summary(user, user_data, techs, data_type, additional_info):
    techs_str = ", ".join(techs)
    techs_tags = " ".join(f"#{tech}" for tech in techs)

    summary_templates = {
        "need_worker": (
            f"<b>Xodim kerak</b>\n\n"
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
            f"#xodim_kerak {techs_tags} #{additional_info['region_tag']}"
        ),
        # Add templates for other data types as required
    }

    return summary_templates.get(data_type, "No summary template found")


# Fetch and send user information to channel
async def get_send_user_info(user_id, data_type):
    user = await db.get_entry("users", "telegram_id", user_id)
    user_data = await db.get_entry("users_data", "user_id", user['id'])

    technologies = await db.get_entries("user_techs", "user_id", user['id'])
    techs = [(await db.get_entry("technologies", "id", tech['id']))['technology_name'] for tech in technologies]

    additional_info = {}
    if data_type == "need_worker":
        idora = await db.get_entry("idoralar", "user_id", user['id'])
        worker = await db.get_entry(data_type, "idora_id", idora['id'])
        region = (await db.get_entry("regions", "id", idora['region_id']))['region_name']
        additional_info = {
            "idora_nomi": idora['idora_nomi'],
            "masul": idora['masul'],
            "region": region,
            "m_vaqti": worker['m_vaqti'],
            "i_vaqti": worker['i_vaqti'],
            "maosh": worker['maosh'],
            "qoshimcha": idora['qoshimcha'],
            "region_tag": region.split(",")[0].split(" ")[0]
        }

    summary = await generate_summary(user, user_data, techs, data_type, additional_info)
    await bot.send_message(CHANNEL, summary)


# Delete all user-related data
async def delete_user_data(telegram_id, call, department, row_id):
    try:
        user_id = (await db.get_entry("users", "telegram_id", telegram_id))['id']
        await db.delete_from_table("users_data", "user_id", user_id)
        await db.delete_from_table("user_techs", "user_id", user_id)

        if department == "need_worker":
            idora_id = (await db.get_entry(department, "id", row_id))['idora_id']
            await db.delete_from_table("idoralar", "id", idora_id)
            await db.delete_from_table(department, "id", row_id)
        else:
            await db.delete_from_table(department, "user_id", user_id)
    except Exception as err:
        await call.message.edit_text(f"Error: {err}")


# Handle admin approval of request
@router.callback_query(F.data.startswith('admincheck_yes:'))
async def admincheck_approve(call: types.CallbackQuery):
    user_telegram, row_id, department = split_data(call.data)
    if department in chapters:
        text = f"Sizning {chapters[department]} bo'limi uchun yuborgan {user_telegram}{row_id} raqamli so'rovingiz qabul qilindi!"
        await get_send_user_info(user_telegram, department)
        await send_and_alert(user_telegram, text, call)


# Prompt for rejection reason
@router.callback_query(F.data.startswith("admincheck_no:"))
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
        f"Sizning <b>{chapters[data['ck_department']]}</b> bo'limi uchun yuborgan {data['ck_telegram']}{data['ck_row']} "
        f"raqamli so'rovingiz rad etildi!\n\nSabab: {data['ck_text']}")
    await send_and_alert(data['ck_telegram'], rejection_message, call)
    await delete_user_data(data['ck_telegram'], call, data['ck_department'], int(data['ck_row']))
    await state.clear()
