from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from bot.keyboards.reply.users_dkb import check_dkb
from bot.states.user_states import JobSearch

router = Router()


async def js_datas(message: types.Message, state: FSMContext, save_to_db: bool = False):
    data = await state.get_data()
    techs_ = " ".join(f"#{tech.strip().lower()}" for tech in data['js_technologies'].split(","))
    region = data['js_region'].split(" ")[0]

    if save_to_db:
        return data
    else:
        text = (f"👨‍💼 <b>Xodim:</b> {data['js_fullname']}\n"
                f"🕑 <b>Yosh:</b> {data['js_age']}\n"
                f"🧑‍💻 <b>Texnologiya:</b> {data['js_technologies']}\n"
                f"🔗 <b>Telegram:</b> @{message.from_user.username}\n"
                f"📞 <b>Aloqa</b> {data['js_phone']}\n"
                f"🌎 <b>Hudud:</b> {data['js_region']}\n"
                f"💰 <b>Narx:</b> {data['js_cost']}\n"
                f"💻 <b>Kasbi:</b> {data['js_profession']}\n"
                f"⌚️ <b>Murojaat qilish vaqti:</b> {data['js_apply_time']}\n"
                f"📌 <b>Maqsad:</b> {data['js_maqsad']}\n\n"
                f"#xodim {techs_} #{region}")
        return text


async def collect_info(message: types.Message, state: FSMContext, next_state, question, data_key, markup=None):
    await state.update_data({data_key: message.text})
    if markup:
        await message.answer(text=question, reply_markup=markup)
    else:
        await message.answer(text=question)
    await state.set_state(next_state)


@router.message(F.text == 'Ish joyi kerak')
async def js_ish_joyi_kerak(message: types.Message, state: FSMContext):
    await message.answer("👤 Ism sharifingizni kiriting:\n\n<b>Namuna: Birnarsa Birnarsayev</b>")
    await state.set_state(JobSearch.full_name)


@router.message(JobSearch.full_name)
async def js_full_name(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.age,
                       "Yoshingizni kiriting:\n\n<b>Namuna: 20</b>", 'js_fullname')


@router.message(JobSearch.age)
async def js_age(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.technology,
                       "<b>🧑‍💻 Texnologiya</b>\n\nBiladigan texnologiyalaringizni kiriting (texnologiya "
                       "nomlarini vergul bilan ajrating).\n\n<b>Namuna: Java, Python, C++</b>",
                       'js_age')


@router.message(JobSearch.technology)
async def js_technology(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.phone,
                       "📞 <b>Aloqa</b>:\n\nBog'lanish uchun telefon raqamingizni kiriting\n\n<b>Namuna: "
                       "+998971234567</b>", 'js_technologies')


@router.message(JobSearch.phone)
async def js_phone(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.region,
                       "🌎 Hududingiz qaysi?\n\n(O'zbekistonda bo'lsangiz viloyat va shahar nomini, chet elda "
                       "bo'lsangiz davlat va shahar nomini kiriting)\n\n<b>Namuna: "
                       "Farg'ona, Qo'qon yoki Turkiya, Istanbul</b>", 'js_phone')


@router.message(JobSearch.region)
async def js_region(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.cost,
                       "💰 <b>Narxi:</b>\n\nKutilayotgan narxni kiriting:\n\n<b>Namuna: 15.000.000 so'm "
                       "yoki $10.000</b>", 'js_region')


@router.message(JobSearch.cost)
async def js_cost(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.profession,
                       "👨🏻‍💻 <b>Kasbi:</b>\n\nKasbingiz va darajangizni kiriting:\n\n<b>Namuna: Python Developer, "
                       "Senior</b>", 'js_cost')


@router.message(JobSearch.profession)
async def js_profession(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.apply_time,
                       "🕰 <b>Murojaat qilish vaqti:</b>\n\nQaysi vaqt oralig'ida murojaat qilish mumkin?"
                       "\n\n<b>Namuna: 09:00 - 21:00</b>", 'js_profession')


@router.message(JobSearch.apply_time)
async def js_apply_time(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.maqsad,
                       "📌 <b>Maqsad:</b>\n\nMaqsadingizni qisqacha yozing", 'js_apply_time')


@router.message(JobSearch.maqsad)
async def js_maqsad(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.check,
                       f"Kiritilgan barcha ma'lumotlarni tekshirib kerakli tugmani bosing", 'js_maqsad',
                       check_dkb)
    data = await js_datas(message, state)
    await message.answer(data)


@router.message(JobSearch.check)
async def js_check(message: types.Message, state: FSMContext):
    confirmation = message.text

    if confirmation == "♻️ Qayta kiritish":
        await js_ish_joyi_kerak(message, state)
    elif confirmation == "✅ Tasdiqlash":
        data = await js_datas(message, state, save_to_db=True)
        print(data)
        # Ma'lumotlarni saqlash bo'limi
        await message.answer("Ma'lumotlaringiz saqlandi!")
