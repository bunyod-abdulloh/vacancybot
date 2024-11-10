from aiogram import Router, types, F

router = Router()

text = ["👤 Ism sharifingizni kiriting:\n\n<b>Namuna: Birnarsa Birnarsayev</b>",
        "🕑 Yoshingizni kiriting:\n\n<b>Namuna: 20</b>",
        "<b>🧑‍💻 Texnologiya</b>\n\nKerakli texnologiyalarni kiriting (vergul bilan ajrating).\n\n"
        "<b>Namuna: Java, Python, C++</b>",
        "📞 <b>Aloqa</b>:\n\nTelefon raqamingizni kiriting\n\n<b>Namuna: +998971234567</b>",
        "🌎 Hududingizni kiriting (viloyat/shahar yoki davlat/shahar nomi)\n\n<b>Namuna: Farg'ona, Qo'qon yoki "
        "Turkiya, Istanbul</b>",
        "💰 <b>Narxi:</b>\n\nTo'lov qilsangiz narxni yozing, amaliyot/tajriba uchun bo'lsa bittasini yozing:"
        "👨🏻‍💻 <b>Kasbi:</b>\n\nIshlaysizmi yoki o'qiysizmi? (o'qisangiz o'quvchi/talaba, ishlasangiz lavozim/darajangizni kiriting)",
        "🕰 <b>Murojaat qilish vaqti:</b>\n\nMurojaat qilish vaqtini kiriting:\n\n<b>Namuna: 09:00 - 21:00</b>",
        "📌 <b>Maqsad:</b>\n\nMaqsadingizni yozing"]


@router.message(F.text == "Ustoz kerak")
async def need_teacher_main(message: types.Message):
    pass


import traceback

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.reply.users_dkb import check_dkb
from loader import bot

router = Router()


# Define state class with stages
class MentorRequest(StatesGroup):
    collecting_data = State()
    check = State()


# Questions and corresponding keys for each step
mentor_questions = [
    ("👤 Ism sharifingizni kiriting:\n\n<b>Namuna: Birnarsa Birnarsayev</b>", 'mr_fullname'),
    ("🕑 Yoshingizni kiriting:\n\n<b>Namuna: 20</b>", 'mr_age'),
    (
        "<b>🧑‍💻 Texnologiya</b>\n\nTexnologiyalaringizni kiriting (vergul bilan ajrating).\n\n<b>Namuna: Java, Python, C++</b>",
        'mr_technologies'),
    ("📞 <b>Aloqa</b>:\n\nTelefon raqamingizni kiriting\n\n<b>Namuna: +998971234567</b>", 'mr_phone'),
    (
        "🌎 Hududingizni kiriting (viloyat/shahar yoki davlat/shahar nomi)\n\n<b>Namuna: Farg'ona, Qo'qon yoki Turkiya, Istanbul</b>",
        'mr_region'),
    ("💰 <b>Narxi:</b>\n\nTo'lov qilsangiz narxni yozing, amaliyot/tajriba uchun bo'lsa bittasini yozing:", 'mr_cost'),
    (
        "👨🏻‍💻 <b>Kasbi:</b>\n\nO'qisangiz talaba/o'quvchi, ishlasangiz lavozim/darajangizni kiriting:\n\n<b>Namuna: Python Developer, Senior</b>",
        'mr_profession'),
    ("🕰 <b>Murojaat qilish vaqti:</b>\n\nMurojaat qilish vaqtini kiriting:\n\n<b>Namuna: 09:00 - 21:00</b>",
     'mr_apply_time'),
    ("📌 <b>Maqsad:</b>\n\nMaqsadingizni yozing", 'mr_goal')
]


# Optimized data formatting function
async def format_mentor_data(data: dict, username: str):
    techs = " ".join(f"#{tech.strip().lower()}" for tech in data['mr_technologies'].split(","))
    region = data['mr_region'].split(",")[0].split(" ")[0]
    return (
        f"👨‍💼 <b>Shogird:</b> {data['mr_fullname']}\n"
        f"🕑 <b>Yosh:</b> {data['mr_age']}\n"
        f"🧑‍💻 <b>Texnologiyalar:</b> {data['mr_technologies']}\n"
        f"🔗 <b>Telegram:</b> @{username}\n"
        f"📞 <b>Aloqa:</b> {data['mr_phone']}\n"
        f"🌎 <b>Hudud:</b> {data['mr_region']}\n"
        f"💰 <b>Narxi:</b> {data['mr_cost']}\n"
        f"💻 <b>Kasbi:</b> {data['mr_profession']}\n"
        f"⌚️ <b>Murojaat qilish vaqti:</b> {data['mr_apply_time']}\n"
        f"📌 <b>Maqsad:</b> {data['mr_goal']}\n\n"
        f"#ustoz_kerak {techs} #{region}"
    )


# Start handler for mentor request
@router.message(F.text == 'Ustoz kerak')
async def mentor_request_start(message: types.Message, state: FSMContext):
    await message.answer(mentor_questions[0][0])
    await state.update_data(mr_index=0)
    await state.set_state(MentorRequest.collecting_data)


# Unified handler for sequential data collection
@router.message(MentorRequest.collecting_data)
async def collect_mentor_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    mr_index = data.get("mr_index", 0)

    # Validating age input
    if mentor_questions[mr_index][1] == 'mr_age' and not (message.text.isdigit() and len(message.text) == 2):
        await message.answer("Namunada ko'rsatilganidek ikki honali son kiriting!")
        return

    # Save current response
    await state.update_data({mentor_questions[mr_index][1]: message.text})

    # Move to the next question or end
    if mr_index + 1 < len(mentor_questions):
        next_mr = mentor_questions[mr_index + 1][0]
        await message.answer(next_mr)
        await state.update_data(mr_index=mr_index + 1)
    else:
        # Data collection completed
        data_ = await state.get_data()
        user_data = await format_mentor_data(data=data_, username=message.from_user.username)
        await message.answer(f"Kiritilgan ma'lumotlarni tekshiring\n\n{user_data}", reply_markup=check_dkb)
        await state.set_state(MentorRequest.check)


# Check and confirm handler
@router.message(MentorRequest.check)
async def mentor_request_check(message: types.Message, state: FSMContext):
    if message.text == "♻️ Qayta kiritish":
        await mentor_request_start(message, state)
    elif message.text == "✅ Tasdiqlash":
        try:
            data = await state.get_data()
            telegram_id = message.from_user.id
            print(data)
            # region_id = (await db.add_entry("regions", "region_name", data['mr_region']))['id']
            # user_id = (await db.add_user(telegram_id, data['mr_age'], region_id=region_id))['id']
            # await db.add_user_datas(user_id=user_id, full_name=data['mr_fullname'],
            #                         username=f'@{message.from_user.username}', phone=data['mr_phone'])
            # profession_id = (await db.add_entry("professions", "profession_name", data['mr_profession']))['id']
            # technology_ids = [
            #     (await db.add_entry("technologies", "technology_name", tech.strip()))['id']
            #     for tech in data['mr_technologies'].split(",")
            # ]
            #
            # await db.add_technologies(user_id=user_id, technology_ids=technology_ids)
            # job_id = (await db.add_srch_job(user_id, profession_id, data['mr_apply_time'], data['mr_cost'],
            #                                 data['mr_goal']))['id']
            #
            # await message.answer(
            #     f"Ma'lumotlaringiz adminga yuborildi!\n\nSo'rov raqami: {telegram_id}{job_id}"
            #     f"\n\nAdmin tekshirib chiqqanidan so'ng natija yuboriladi!",
            #     reply_markup=main_dkb())
            #
            # await bot.send_message(ADMIN_GROUP, f"Ustoz kerak bo'limiga yangi murojaat kelib tushdi!\n\n"
            #                                     f"{await format_mentor_data(data, message.from_user.username)}",
            #                        reply_markup=first_check_ikb(telegram_id=telegram_id, row_id=job_id,
            #                                                     department="Ustoz kerak"))
            # await state.clear()
        except Exception as err:
            tb = traceback.format_tb(err.__traceback__)
            trace = tb[0]
            bot_properties = await bot.me()
            bot_message = f"Bot: {bot_properties.full_name}"

            await message.answer(text=f"{bot_message}\n\nXatolik:\n{trace}\n\n{err}")

    else:
        await message.answer(
            text="Faqat <b>✅ Tasdiqlash</b> yoki <b>♻️ Qayta kiritish</b> buyruqlari kiritilishi lozim!")
