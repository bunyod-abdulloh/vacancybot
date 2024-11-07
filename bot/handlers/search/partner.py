from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline.admin_ikb import first_check_ikb
from bot.keyboards.reply.main_dkb import main_dkb
from bot.keyboards.reply.users_dkb import check_dkb
from bot.states.user_states import LookingPartner
from data.config import BIG_ADMIN
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
    region = data['region'].split(" ")[0]

    if save_to_db:
        return data

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
    LookingPartner.phone: ("phone", "🌎 Hududingiz qaysi? (O'zbekistonda..."),
    LookingPartner.region: ("region", "💰 <b>Narxi:</b>\n\nTo'lov qilasizmi yoki bepulmi?..."),
    LookingPartner.cost: ("cost", "👨🏻‍💻 <b>Kasbi:</b>\n\nKasbingiz va darajangiz?"),
    LookingPartner.profession: ("profession", "🕰 <b>Murojaat qilish vaqti:</b>\n\nQaysi vaqt oralig'ida..."),
    LookingPartner.apply_time: ("apply_time", "📌 <b>Maqsad:</b>\n\nMaqsadingizni qisqacha yozing")
}


@router.message(F.text & state_questions)
async def handle_state_data(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    data_key, question = state_questions[current_state]
    next_state = list(state_questions.keys())[list(state_questions.keys()).index(current_state) + 1]
    await collect_data(message, state, next_state, question, data_key)


@router.message(LookingPartner.maqsad)
async def finalize_partner_data(message: types.Message, state: FSMContext):
    await state.update_data(maqsad=message.text)
    data_text = await partner_data_text(message, state)
    await message.answer(text=data_text)
    await message.answer(text="Kiritilgan barcha ma'lumotlarni tekshirib kerakli tugmani bosing",
                         reply_markup=check_dkb)
    await state.set_state(LookingPartner.check)


@router.message(LookingPartner.check)
async def confirm_or_reenter_data(message: types.Message, state: FSMContext):
    if message.text == "♻️ Qayta kiritish":
        await start_partner_search(message, state)
    elif message.text == "✅ Tasdiqlash":
        data = await partner_data_text(message, state, save_to_db=True)
        user = await db.add_user(telegram_id=message.from_user.id, username=f'@{message.from_user.username}',
                                 full_name=data['fullname'], phone=data['phone'], age=None)
        region = await db.add_entry("regions", "region_name", data['region'])
        profession = await db.add_entry("professions", "profession_name", data['profession'])
        technology_ids = [await db.add_entry("technologies", "technology_name", tech.strip().lower())['id']
                          for tech in data['technologies'].split(",")]

        await db.add_technologies(user_id=user['id'], technology_ids=technology_ids)
        search_id = await db.add_srch_partner(user_id=user['id'], region_id=region['id'],
                                              profession_id=profession['id'],
                                              apply_time=data['apply_time'], cost=data['cost'], maqsad=data['maqsad'])

        confirmation_text = (f"Ma'lumotlaringiz adminga yuborildi!\n\n"
                             f"So'rov raqami: {message.from_user.id}{search_id['id']}\n\n"
                             f"Admin tekshirib chiqqanidan so'ng natija yuboriladi!")
        await message.answer(text=confirmation_text, reply_markup=main_dkb())
        data_text = await partner_data_text(message, state)
        await bot.send_message(chat_id=BIG_ADMIN,
                               text=f"Sherik kerak bo'limiga yangi habar qabul qilindi!\n\n{data_text}",
                               reply_markup=first_check_ikb(telegram_id=message.from_user.id, row_id=search_id['id'],
                                                            department="Sherik kerak"))
        await state.clear()
    else:
        await state.clear()
