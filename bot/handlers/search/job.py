import traceback

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.inline.admin_ikb import first_check_ikb
from bot.keyboards.reply.main_dkb import main_dkb
from bot.keyboards.reply.users_dkb import check_dkb
from data.config import ADMIN_GROUP
from loader import db, bot

router = Router()


# Define state class with stages
class JobSearch(StatesGroup):
    collecting_data = State()
    check = State()


# Questions and corresponding keys for each step
questions = [
    ("👤 Ism sharifingizni kiriting:\n\n<b>Namuna: Birnarsa Birnarsayev</b>", 'js_fullname'),
    ("Yoshingizni kiriting:\n\n<b>Namuna: 20</b>", 'js_age'),
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
async def format_user_data(data: dict, username: str):
    techs = " ".join(f"#{tech.strip().lower()}" for tech in data['js_technologies'].split(","))
    region = data['js_region'].split(",")[0].split(" ")[0]
    return (
        f"👨‍💼 <b>Xodim:</b> {data['js_fullname']}\n"
        f"🕑 <b>Yosh:</b> {data['js_age']}\n"
        f"🧑‍💻 <b>Texnologiya:</b> {data['js_technologies']}\n"
        f"🔗 <b>Telegram:</b> @{username}\n"
        f"📞 <b>Aloqa</b> {data['js_phone']}\n"
        f"🌎 <b>Hudud:</b> {data['js_region']}\n"
        f"💰 <b>Narx:</b> {data['js_cost']}\n"
        f"💻 <b>Kasbi:</b> {data['js_profession']}\n"
        f"⌚️ <b>Murojaat qilish vaqti:</b> {data['js_apply_time']}\n"
        f"📌 <b>Maqsad:</b> {data['js_maqsad']}\n\n"
        f"#xodim {techs} #{region}"
    )


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
        await message.answer("Kiritilgan ma'lumotlarni tekshiring", reply_markup=check_dkb)
        await state.set_state(JobSearch.check)


# Check and confirm handler
@router.message(JobSearch.check)
async def js_check(message: types.Message, state: FSMContext):
    if message.text == "♻️ Qayta kiritish":
        await js_ish_joyi_kerak(message, state)
    elif message.text == "✅ Tasdiqlash":
        try:
            data = await state.get_data()
            telegram_id = message.from_user.id
            region_id = (await db.add_entry("regions", "region_name", data['js_region']))['id']
            user_id = (await db.add_user(telegram_id, data['js_age'], region_id=region_id))['id']
            await db.add_user_datas(user_id=user_id, full_name=data['js_fullname'],
                                    username=f'@{message.from_user.username}', phone=data['js_phone'])
            profession_id = (await db.add_entry("professions", "profession_name", data['js_profession']))['id']
            technology_ids = [
                (await db.add_entry("technologies", "technology_name", tech.strip()))['id']
                for tech in data['js_technologies'].split(",")
            ]

            await db.add_technologies(user_id=user_id, technology_ids=technology_ids)
            job_id = (await db.add_srch_job(user_id, profession_id, data['js_apply_time'], data['js_cost'],
                                            data['js_maqsad']))['id']

            await message.answer(
                f"Ma'lumotlaringiz adminga yuborildi!\n\nSo'rov raqami: {telegram_id}{job_id}"
                f"\n\nAdmin tekshirib chiqqanidan so'ng natija yuboriladi!",
                reply_markup=main_dkb())

            await bot.send_message(ADMIN_GROUP, f"Ish joyi kerak bo'limiga yangi habar qabul qilindi!\n\n"
                                                f"{await format_user_data(data, message.from_user.username)}",
                                   reply_markup=first_check_ikb(telegram_id=telegram_id, row_id=job_id,
                                                                department="Ish joyi kerak"))
            await state.clear()
        except Exception as err:
            tb = traceback.format_tb(err.__traceback__)
            trace = tb[0]
            bot_properties = await bot.me()
            bot_message = f"Bot: {bot_properties.full_name}"

            await message.answer(text=f"{bot_message}\n\nXatolik:\n{trace}\n\n{err}")

    else:
        await message.answer(
            text="Faqat <b>✅ Tasdiqlash</b> yoki <b>♻️ Qayta kiritish</b> buyruqlari kiritilishi lozim!")
