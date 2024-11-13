from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.handlers.functions.functions_one import failed_message, warning_message, send_to_admin
from bot.keyboards.reply.main_dkb import main_dkb
from bot.keyboards.reply.users_dkb import check_dkb
from loader import db

router = Router()


# Define state class with stages
class JobSearch(StatesGroup):
    collecting_data = State()
    check = State()


# Questions and corresponding keys for each step
questions = [
    ("👤 Ism sharifingizni kiriting:\n\n<b>Namuna: Birnarsa Birnarsayev</b>", 'js_fullname'),
    ("🕑 Yoshingizni kiriting:\n\n<b>Namuna: 20</b>", 'js_age'),
    ("<b>🧑‍💻 Texnologiya</b>\n\nTexnologiyalaringizni kiriting (vergul bilan ajrating).\n\n"
     "<b>Namuna: Java, Python, C++</b>", 'js_technologies'),
    ("📞 <b>Aloqa</b>:\n\nTelefon raqamingizni kiriting\n\n<b>Namuna: +998971234567</b>", 'js_phone'),
    ("🌎 Hududingizni kiriting (viloyat/shahar yoki davlat/shahar nomi)\n\n<b>Namuna: Farg'ona, Qo'qon yoki "
     "Turkiya, Istanbul</b>", 'js_region'),
    ("💰 <b>Narxi:</b>\n\nKutilayotgan narxni kiriting:\n\n<b>Namuna: 15.000.000 so'm, "
     "$10.000 yoki amaliyot/tajriba uchun</b>", 'js_cost'),
    ("👨🏻‍💻 <b>Kasbi:</b>\n\nKasbingiz va darajangizni kiriting:\n\n<b>Namuna: Python Developer, Senior</b>",
     'js_profession'),
    ("🕰 <b>Murojaat qilish vaqti:</b>\n\nMurojaat qilish vaqtini kiriting:\n\n<b>Namuna: 09:00 - 21:00</b>",
     'js_apply_time'),
    ("📌 <b>Maqsad:</b>\n\nMaqsadingizni yozing", 'js_maqsad')
]


# Optimized data formatting function
async def format_user_data(data: dict, message: types.Message, to_user=False, to_admin=False, row_id=None):
    techs = " ".join(f"#{tech.strip().lower()}" for tech in data['js_technologies'].split(","))
    region = data['js_region'].split(",")[0].split(" ")[0]
    summary = (
        f"👨‍💼 <b>Xodim:</b> {data['js_fullname']}\n"
        f"🕑 <b>Yosh:</b> {data['js_age']}\n"
        f"🧑‍💻 <b>Texnologiya:</b> {data['js_technologies']}\n"
        f"🔗 <b>Telegram:</b> @{message.from_user.username}\n"
        f"📞 <b>Aloqa</b> {data['js_phone']}\n"
        f"🌎 <b>Hudud:</b> {data['js_region']}\n"
        f"💰 <b>Narx:</b> {data['js_cost']}\n"
        f"💻 <b>Kasbi:</b> {data['js_profession']}\n"
        f"⌚️ <b>Murojaat qilish vaqti:</b> {data['js_apply_time']}\n"
        f"📌 <b>Maqsad:</b> {data['js_maqsad']}\n\n"
        f"#xodim {techs} #{region}"
    )
    if to_user:
        await message.answer(text=summary)
    if to_admin:
        await send_to_admin(chapter="Ish joyi kerak", row_id=row_id, telegram_id=message.from_user.id, summary=summary,
                            department="need_job")


# Start handler
@router.message(F.text == 'Ish joyi kerak')
async def js_ish_joyi_kerak(message: types.Message, state: FSMContext):
    await message.answer(questions[0][0])
    await state.update_data(prompt_index=0)
    await state.set_state(JobSearch.collecting_data)


# Unified handler for sequential data collection
@router.message(JobSearch.collecting_data)
async def collect_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    prompt_index = data.get("prompt_index", 0)

    # Validating age input
    if questions[prompt_index][1] == 'js_age' and not (message.text.isdigit() and len(message.text) == 2):
        await message.answer("Namunada ko'rsatilganidek ikki honali son kiriting!")
        return

    # Save current response
    await state.update_data({questions[prompt_index][1]: message.text})

    # Move to the next question or end
    if prompt_index + 1 < len(questions):
        next_prompt = questions[prompt_index + 1][0]
        await message.answer(next_prompt)
        await state.update_data(prompt_index=prompt_index + 1)
    else:
        # Data collection completed
        data_ = await state.get_data()
        await format_user_data(data=data_, message=message, to_user=True)
        await message.answer(f"Kiritilgan ma'lumotlarni tekshirib, kerakli tugmani bosing", reply_markup=check_dkb)
        await state.set_state(JobSearch.check)


# Check and confirm handler
@router.message(JobSearch.check)
async def js_check(message: types.Message, state: FSMContext):
    if message.text == "♻️ Qayta kiritish":
        await js_ish_joyi_kerak(message, state)
    elif message.text == "✅ Tasdiqlash":
        try:
            data = await state.get_data()
            user_id = (await db.add_user(message.from_user.id))['id']
            await db.add_user_datas(user_id=user_id, full_name=data['js_fullname'],
                                    username=f'@{message.from_user.username}', age=data['js_age'],
                                    phone=data['js_phone'])
            region_id = (await db.add_entry(table="regions", field="region_name", value=data['js_region']))['id']
            profession_id = (
                await db.add_entry(table="professions", field="profession", value=data['js_profession']))['id']
            job_id = (
                await db.add_srch_job(user_id=user_id, profession_id=profession_id, apply_time=data['js_apply_time'],
                                      cost=data['js_cost'], maqsad=data['js_maqsad'], region_id=region_id))['id']
            for tech in data['js_technologies'].split(","):
                tech_id = (await db.add_entry("technologies", "technology_name", tech.strip()))['id']
                await db.add_technologies(user_id=job_id, technology_id=tech_id, table_name="need_job")
            await format_user_data(data=data, message=message, to_admin=True, row_id=job_id)
            await message.answer(
                f"Ma'lumotlaringiz adminga yuborildi!\n\nSo'rov raqami: {message.from_user.id}{job_id}"
                f"\n\nAdmin tekshirib chiqqanidan so'ng natija yuboriladi!",
                reply_markup=main_dkb())
            await state.clear()
        except Exception as err:
            await failed_message(message, err)
    else:
        await warning_message(message)
