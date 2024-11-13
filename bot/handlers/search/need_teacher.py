from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.handlers.functions.functions_one import failed_message, warning_message, send_to_admin
from bot.keyboards.reply.main_dkb import main_dkb
from bot.keyboards.reply.users_dkb import check_dkb
from loader import db

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
async def format_mentor_data(data: dict, message: types.Message, to_user=False, to_admin=False, row_id=None):
    techs = " ".join(f"#{tech.strip().lower()}" for tech in data['mr_technologies'].split(","))
    region = data['mr_region'].split(",")[0].split(" ")[0]
    summary = (
        f"<b>Ustoz kerak</b>\n\n"
        f"👨‍💼 <b>Shogird:</b> {data['mr_fullname']}\n"
        f"🕑 <b>Yosh:</b> {data['mr_age']}\n"
        f"🧑‍💻 <b>Texnologiyalar:</b> {data['mr_technologies']}\n"
        f"🔗 <b>Telegram:</b> @{message.from_user.username}\n"
        f"📞 <b>Aloqa:</b> {data['mr_phone']}\n"
        f"🌎 <b>Hudud:</b> {data['mr_region']}\n"
        f"💰 <b>Narxi:</b> {data['mr_cost']}\n"
        f"💻 <b>Kasbi:</b> {data['mr_profession']}\n"
        f"⌚️ <b>Murojaat qilish vaqti:</b> {data['mr_apply_time']}\n"
        f"📌 <b>Maqsad:</b> {data['mr_goal']}\n\n"
        f"#ustoz_kerak {techs} #{region}"
    )
    if to_user:
        await message.answer(summary)
    if to_admin:
        await send_to_admin(chapter="Ustoz kerak", row_id=row_id, telegram_id=message.from_user.id, summary=summary,
                            department="need_teacher")


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
        await format_mentor_data(data=data_, message=message, to_user=True)
        await message.answer(f"Kiritilgan ma'lumotlarni tekshirib, kerakli tugmani bosing", reply_markup=check_dkb)
        await state.set_state(MentorRequest.check)


# Check and confirm handler
@router.message(MentorRequest.check)
async def mentor_request_check(message: types.Message, state: FSMContext):
    if message.text == "♻️ Qayta kiritish":
        await mentor_request_start(message, state)
    elif message.text == "✅ Tasdiqlash":
        try:
            data = await state.get_data()
            user_id = (await db.add_user(telegram_id=message.from_user.id))['id']
            await db.add_user_datas(user_id=user_id, full_name=data['mr_fullname'],
                                    username=f'@{message.from_user.username}', age=data['mr_age'],
                                    phone=data['mr_phone'])
            region_id = (await db.add_entry("regions", "region_name", data['mr_region']))['id']
            profession_id = (await db.add_entry("professions", "profession", data['mr_profession']))['id']
            id_ = (await db.add_need_teacher(user_id=user_id, profession_id=profession_id,
                                             apply_time=data['mr_apply_time'], cost=data['mr_cost'],
                                             maqsad=data['mr_goal'], region_id=region_id))['id']
            for tech in data['mr_technologies'].split(","):
                tech_id = (await db.add_entry(table="technologies", field="technology_name", value=tech.strip()))['id']
                await db.add_technologies(user_id=id_, technology_id=tech_id, table_name="need_teacher")
            await format_mentor_data(data=data, message=message, to_admin=True, row_id=id_)
            await message.answer(
                f"Ma'lumotlaringiz adminga yuborildi!\n\nSo'rov raqami: {message.from_user.id}{id_}"
                f"\n\nAdmin tekshirib chiqqanidan so'ng natija yuboriladi!",
                reply_markup=main_dkb())
            await state.clear()
        except Exception as err:
            await failed_message(message, err)
    else:
        await warning_message(message)
