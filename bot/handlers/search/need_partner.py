from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.handlers.functions.functions_one import failed_message, warning_message, send_to_admin
from bot.keyboards.reply.main_dkb import main_dkb
from bot.keyboards.reply.users_dkb import check_dkb
from bot.states.user_states import LookingPartner
from loader import db

router = Router()


# Common function to collect user data and move to the next state
async def collect_data(message: types.Message, state: FSMContext, next_state, question, data_key):
    await state.update_data({data_key: message.text})
    await message.answer(text=question)
    await state.set_state(next_state)


# Generates the partner data message for review or database storage
async def partner_data_text(data: dict, message: types.Message, to_user=False, to_admin=False,
                            row_id=None):
    techs = " ".join(f"#{tech.strip().lower()}" for tech in data['pr_technologies'].split(","))
    region = data['pr_region'].split(",")[0].split(" ")[0]
    summary = (f"<b>Sherik kerak</b>\n\n"
               f"👤 <b>Sherik:</b> {data['pr_fullname']}\n"
               f"🧑‍💻 <b>Texnologiya:</b> {data['pr_technologies']}\n"
               f"🔗 <b>Telegram:</b> @{message.from_user.username}\n"
               f"📞 <b>Aloqa:</b> {data['pr_phone']}\n"
               f"🌎 <b>Hudud:</b> {data['pr_region']}\n"
               f"💰 <b>Narx:</b> {data['pr_cost']}\n"
               f"💻 <b>Kasbi:</b> {data['pr_profession']}\n"
               f"⌚️ <b>Murojaat qilish vaqti:</b> {data['pr_apply_time']}\n"
               f"📌 <b>Maqsad:</b> {data['pr_maqsad']}\n\n"
               f"#sherik {techs} #{region}")
    if to_user:
        await message.answer(text=summary)
    if to_admin:
        await send_to_admin(chapter="Sherik kerak", row_id=row_id, telegram_id=message.from_user.id, summary=summary,
                            department="need_partner")


@router.message(F.text == "Sherik kerak")
async def start_partner_search(message: types.Message, state: FSMContext):
    await collect_data(message, state, LookingPartner.fullname,
                       "👤 Ism sharifingizni kiriting:\n\n<b>Namuna: Birnarsa Birnarsayev</b>", 'fullname')


# Define the state transitions and their questions
state_questions = {
    LookingPartner.fullname: (
        "pr_fullname", "<b>🧑‍💻 Texnologiya</b>\n\nTalab qilinadigan texnologiyalarni kiriting..."),
    LookingPartner.technology: (
        "pr_technologies", "📞 <b>Aloqa</b>:\n\nBog'lanish uchun telefon raqamingizni kiriting..."),
    LookingPartner.phone: (
        "pr_phone",
        "🌎 Hududingizni kiriting (viloyat/shahar yoki davlat/shahar nomi)\n\n<b>Namuna: Farg'ona, Qo'qon yoki "
        "Turkiya, Istanbul</b>"),
    LookingPartner.region: (
        "pr_region",
        "💰 <b>Narxi:</b>\n\nTo'lov qilasizmi yoki bepulmi?\n\n<b>Namuna: bepul yoki summani kiriting</b>"),
    LookingPartner.cost: (
        "pr_cost",
        "👨🏻‍💻 <b>Kasbi:</b>\n\nKasbingiz va darajangiz?\n\n<b>Namuna: Python Developer, Senior</b>"),
    LookingPartner.profession: (
        "pr_profession", "🕰 <b>Murojaat qilish vaqti:</b>\n\nMurojaat qilish vaqtini kiriting:\n\n"
                         "<b>Namuna: 09:00 - 21:00</b>"),
    LookingPartner.apply_time: ("pr_apply_time", "📌 <b>Maqsad:</b>\n\nMaqsadingizni qisqacha yozing")
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
    await state.update_data(pr_maqsad=message.text)
    data = await state.get_data()
    await partner_data_text(data=data, message=message, to_user=True)
    await message.answer(text="Kiritilgan barcha ma'lumotlarni tekshirib kerakli tugmani bosing",
                         reply_markup=check_dkb)
    await state.set_state(LookingPartner.check)


@router.message(F.text, LookingPartner.check)
async def confirm_or_reenter_data(message: types.Message, state: FSMContext):
    if message.text == "♻️ Qayta kiritish":
        await start_partner_search(message, state)
    elif message.text == "✅ Tasdiqlash":
        try:
            data = await state.get_data()

            # Adding data to the database
            user_id = (await db.add_user(telegram_id=message.from_user.id))['id']
            await db.add_user_datas(user_id=user_id, full_name=data['pr_fullname'],
                                    username=f'@{message.from_user.username}', age=None, phone=data['pr_phone'])

            region_id = (await db.add_entry("regions", "region_name", data['pr_region']))['id']
            profession_id = (await db.add_entry("professions", "profession", data['pr_profession']))['id']
            search_id = (
                await db.add_srch_partner(user_id=user_id, profession_id=profession_id,
                                          apply_time=data['pr_apply_time'],
                                          cost=data['pr_cost'], maqsad=data['pr_maqsad'], region_id=region_id))['id']

            for tech in data['pr_technologies'].split(","):
                tech_id = (await db.add_entry("technologies", "technology_name", tech.strip()))['id']
                await db.add_technologies(user_id=search_id, technology_id=tech_id, table_name="need_partner")
            await partner_data_text(data=data, message=message, to_admin=True, row_id=search_id)
            confirmation_text = (f"Ma'lumotlaringiz adminga yuborildi!\n\n"
                                 f"So'rov raqami: {message.from_user.id}{search_id}\n\n"
                                 f"Admin tekshirib chiqqanidan so'ng natija yuboriladi!")
            await message.answer(text=confirmation_text, reply_markup=main_dkb())

            await state.clear()
        except Exception as err:
            await failed_message(message, err)
    else:
        await warning_message(message)
