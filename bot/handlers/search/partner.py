from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline.admin_ikb import first_check_ikb
from bot.keyboards.reply.main_dkb import main_dkb
from bot.keyboards.reply.users_dkb import check_dkb
from bot.states.user_states import LookingPartner
from data.config import ADMIN_GROUP
from loader import bot, db

router = Router()


# Common function to collect user data and move to the next state
async def collect_data(message: types.Message, state: FSMContext, next_state, question, data_key):
    await state.update_data({data_key: message.text})
    await message.answer(text=question)
    await state.set_state(next_state)


# Generates the partner data message for review or database storage
async def partner_data_text(message: types.Message, state: FSMContext, save_to_db: bool = False):
    data = await state.get_data()
    techs = " ".join(f"#{tech.strip().lower()}" for tech in data['technologies'].split(","))
    region = data['region'].split(" ")[0] or data['region'].split(",")[0]

    return (f"👤 <b>Sherik:</b> {data['fullname']}\n"
            f"🧑‍💻 <b>Texnologiya:</b> {data['technologies']}\n"
            f"🔗 <b>Telegram:</b> @{message.from_user.username}\n"
            f"📞 <b>Aloqa</b> {data['phone']}\n"
            f"🌎 <b>Hudud:</b> {data['region']}\n"
            f"💰 <b>Narx:</b> {data['cost']}\n"
            f"💻 <b>Kasbi:</b> {data['profession']}\n"
            f"⌚️ <b>Murojaat qilish vaqti:</b> {data['apply_time']}\n"
            f"📌 <b>Maqsad:</b> {data['maqsad']}\n\n"
            f"#sherik {techs} #{region}")


@router.message(F.text == "Sherik kerak")
async def start_partner_search(message: types.Message, state: FSMContext):
    await collect_data(message, state, LookingPartner.fullname,
                       "👤 Ism sharifingizni kiriting:\n\n<b>Namuna: Birnarsa Birnarsayev</b>", 'fullname')


# Define the state transitions and their questions
state_questions = {
    LookingPartner.fullname: ("fullname", "<b>🧑‍💻 Texnologiya</b>\n\nTalab qilinadigan texnologiyalarni kiriting..."),
    LookingPartner.technology: ("technologies", "📞 <b>Aloqa</b>:\n\nBog'lanish uchun telefon raqamingizni kiriting..."),
    LookingPartner.phone: (
        "phone",
        "🌎 Hududingizni kiriting (viloyat/shahar yoki davlat/shahar nomi)\n\n<b>Namuna: Farg'ona, Qo'qon yoki "
        "Turkiya, Istanbul</b>"),
    LookingPartner.region: (
        "region", "💰 <b>Narxi:</b>\n\nTo'lov qilasizmi yoki bepulmi?\n\n<b>Namuna: bepul yoki summani kiriting</b>"),
    LookingPartner.cost: (
        "cost", "👨🏻‍💻 <b>Kasbi:</b>\n\nKasbingiz va darajangiz?\n\n<b>Namuna: Python Developer, Senior</b>"),
    LookingPartner.profession: (
        "profession", "🕰 <b>Murojaat qilish vaqti:</b>\n\nMurojaat qilish vaqtini kiriting:\n\n"
                      "<b>Namuna: 09:00 - 21:00</b>"),
    LookingPartner.apply_time: ("apply_time", "📌 <b>Maqsad:</b>\n\nMaqsadingizni qisqacha yozing")
}


# Helper function to check if the current state is in state_questions
async def is_in_state_questions(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    return current_state in state_questions


@router.message(is_in_state_questions)
async def handle_state_data(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    data_key, question = state_questions[current_state]

    # Get the next state based on the order in the state_questions dictionary
    state_keys = list(state_questions.keys())
    current_index = state_keys.index(current_state)
    next_state = state_keys[current_index + 1] if current_index + 1 < len(state_keys) else LookingPartner.maqsad

    await collect_data(message, state, next_state, question, data_key)


@router.message(F.text, LookingPartner.maqsad)
async def finalize_partner_data(message: types.Message, state: FSMContext):
    await state.update_data(maqsad=message.text)
    data_text = await partner_data_text(message, state)
    await message.answer(text=data_text)
    await message.answer(text="Kiritilgan barcha ma'lumotlarni tekshirib kerakli tugmani bosing",
                         reply_markup=check_dkb)
    await state.set_state(LookingPartner.check)


@router.message(F.text, LookingPartner.check)
async def confirm_or_reenter_data(message: types.Message, state: FSMContext):
    if message.text == "♻️ Qayta kiritish":
        await start_partner_search(message, state)
    elif message.text == "✅ Tasdiqlash":
        data = await partner_data_text(message, state, save_to_db=True)

        # Adding data to the database
        user = await db.add_user(telegram_id=message.from_user.id, username=f'@{message.from_user.username}',
                                 full_name=data['fullname'], phone=data['phone'], age=None)
        region = await db.add_entry("regions", "region_name", data['region'])
        profession = await db.add_entry("professions", "profession_name", data['profession'])
        technology_ids = []
        for tech in data['technologies'].split(","):
            tech_entry = await db.add_entry("technologies", "technology_name", tech.strip().lower())
            technology_ids.append(tech_entry['id'])

        await db.add_technologies(user_id=user['id'], technology_ids=technology_ids)
        search_id = await db.add_srch_partner(user_id=user['id'], region_id=region['id'],
                                              profession_id=profession['id'],
                                              apply_time=data['apply_time'], cost=data['cost'], maqsad=data['maqsad'])

        confirmation_text = (f"Ma'lumotlaringiz adminga yuborildi!\n\n"
                             f"So'rov raqami: {message.from_user.id}{search_id['id']}\n\n"
                             f"Admin tekshirib chiqqanidan so'ng natija yuboriladi!")
        await message.answer(text=confirmation_text, reply_markup=main_dkb())

        # Sending admin notification
        data_text = await partner_data_text(message, state)
        await bot.send_message(chat_id=ADMIN_GROUP,
                               text=f"Sherik kerak bo'limiga yangi habar qabul qilindi!\n\n{data_text}",
                               reply_markup=first_check_ikb(telegram_id=message.from_user.id, row_id=search_id['id'],
                                                            department="Sherik kerak"))
        await state.clear()
    else:
        await message.answer(
            text="Faqat <b>✅ Tasdiqlash</b> yoki <b>♻️ Qayta kiritish</b> buyruqlari kiritilishi lozim!")
