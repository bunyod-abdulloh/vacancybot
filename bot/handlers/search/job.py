from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline.admin_ikb import first_check_ikb
from bot.keyboards.reply.main_dkb import main_dkb
from bot.keyboards.reply.users_dkb import check_dkb
from bot.states.user_states import JobSearch
from data.config import ADMIN_GROUP
from loader import db, bot

router = Router()


# Optimized data formatting function
async def format_user_data(data: dict, username: str):
    techs = " ".join(f"#{tech.strip().lower()}" for tech in data['js_technologies'].split(","))
    region = data['js_region'].split(" ")[0] or data['js_region'].split(",")[0]
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


# Optimized collect_info function
async def collect_info(message: types.Message, state: FSMContext, next_state, question, data_key, markup=None):
    await state.update_data({data_key: message.text})
    await message.answer(text=question, reply_markup=markup)
    await state.set_state(next_state)


@router.message(F.text == 'Ish joyi kerak')
async def js_ish_joyi_kerak(message: types.Message, state: FSMContext):
    await message.answer("👤 Ism sharifingizni kiriting:\n\n<b>Namuna: Birnarsa Birnarsayev</b>")
    await state.set_state(JobSearch.full_name)


# Handlers for collecting user information
@router.message(JobSearch.full_name)
async def js_full_name(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.age, "Yoshingizni kiriting:\n\n<b>Namuna: 20</b>",
                       'js_fullname')


@router.message(JobSearch.age)
async def js_age(message: types.Message, state: FSMContext):
    await collect_info(
        message, state, JobSearch.technology,
        "<b>🧑‍💻 Texnologiya</b>\n\nTexnologiyalaringizni kiriting (vergul bilan ajrating).\n\n"
        "<b>Namuna: Java, Python, C++</b>", 'js_age'
    )


@router.message(JobSearch.technology)
async def js_technology(message: types.Message, state: FSMContext):
    await collect_info(
        message, state, JobSearch.phone,
        "📞 <b>Aloqa</b>:\n\nTelefon raqamingizni kiriting\n\n<b>Namuna: +998971234567</b>",
        'js_technologies'
    )


@router.message(JobSearch.phone)
async def js_phone(message: types.Message, state: FSMContext):
    await collect_info(
        message, state, JobSearch.region,
        "🌎 Hududingizni kiriting (viloyat/shahar yoki davlat/shahar nomi)\n\n<b>Namuna: Farg'ona, Qo'qon yoki "
        "Turkiya, Istanbul</b>", 'js_phone'
    )


@router.message(JobSearch.region)
async def js_region(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.cost,
                       "💰 <b>Narxi:</b>\n\nKutilayotgan narxni kiriting:\n\n<b>Namuna: 15.000.000 so'm, "
                       "$10.000 yoki amaliyot/tajriba uchun</b>",
                       'js_region')


@router.message(JobSearch.cost)
async def js_cost(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.profession,
                       "👨🏻‍💻 <b>Kasbi:</b>\n\nKasbingiz va darajangizni kiriting:"
                       "\n\n<b>Namuna: Python Developer, Senior</b>", 'js_cost')


@router.message(JobSearch.profession)
async def js_profession(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.apply_time,
                       "🕰 <b>Murojaat qilish vaqti:</b>\n\nMurojaat qilish vaqtini kiriting:\n\n"
                       "<b>Namuna: 09:00 - 21:00</b>",
                       'js_profession')


@router.message(JobSearch.apply_time)
async def js_apply_time(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.maqsad, "📌 <b>Maqsad:</b>\n\nMaqsadingizni yozing",
                       'js_apply_time')


@router.message(JobSearch.maqsad)
async def js_maqsad(message: types.Message, state: FSMContext):
    await collect_info(message, state, JobSearch.check, "Kiritilgan ma'lumotlarni tekshiring",
                       'js_maqsad', check_dkb)
    data = await state.get_data()
    await message.answer(await format_user_data(data, message.from_user.username))


@router.message(JobSearch.check)
async def js_check(message: types.Message, state: FSMContext):
    if message.text == "♻️ Qayta kiritish":
        await js_ish_joyi_kerak(message, state)
    elif message.text == "✅ Tasdiqlash":
        try:
            data = await state.get_data()
            telegram_id = message.from_user.id
            user_id = (await db.add_user(telegram_id, f'@{message.from_user.username}', message.from_user.full_name,
                                         data['js_phone'], data['js_age']))['id']

            region_id = (await db.add_entry("regions", "region_name", data['js_region']))['id']
            profession_id = (await db.add_entry("professions", "profession_name", data['js_profession']))['id']
            technology_ids = [
                (await db.add_entry("technologies", "technology_name", tech.strip().lower()))['id']
                for tech in data['js_technologies'].split(",")
            ]

            await db.add_technologies(user_id=user_id, technology_ids=technology_ids)
            job_id = (await db.add_srch_job(user_id, region_id, profession_id, data['js_apply_time'], data['js_cost'],
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
            await message.answer(text=f"Xatolik {err}\n\nIltimos, so'rovnomani qayta to'ldiring!",
                                 reply_markup=main_dkb())
    else:
        await state.clear()
        await message.answer("Invalid response")
