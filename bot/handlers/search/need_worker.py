from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.reply.main_dkb import main_dkb
from bot.keyboards.reply.users_dkb import check_dkb
from loader import db

router = Router()

# Define text prompts
text_prompts = [
    "🏢 Idora nomi:",
    "🧑‍💻 Texnologiya\n\nTalab qilinadigan texnologiyalarni kiriting:",
    "📞 Aloqa\n\nBog'lanish uchun telefon raqamingizni kiriting:",
    "🌎 Hududingizni kiriting (viloyat/shahar yoki davlat/shahar nomi)\n\n<b>Namuna: Farg'ona, Qo'qon yoki Turkiya, Istanbul</b>",
    "✍️ Mas'ul ism sharifi:",
    "🕰 Murojaat qilish vaqti\n\nMurojaat qilish vaqtini kiriting:\n\n<b>Namuna: 09:00 - 21:00</b>",
    "🕰 Ish vaqtini kiriting:\n\n<b>Namuna: 09:00 - 17:00</b>",
    "💰 Maoshni kiriting:\n\n<b>Namuna: 15.000.000 so'm</b>",
    "‼️ Qo'shimcha ma'lumotlar:"
]


# Define states
class NeedWorkerStates(StatesGroup):
    collecting_data = State()
    check = State()


# Start handler
@router.message(F.text == "Hodim kerak")
async def need_worker_main(message: types.Message, state: FSMContext):
    await message.answer(text_prompts[0])  # Start with the first prompt
    await state.update_data(prompt_index=0)  # Initialize prompt index
    await state.set_state(NeedWorkerStates.collecting_data)


# Unified handler for sequential data collection
@router.message(NeedWorkerStates.collecting_data)
async def collect_worker_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    prompt_index = data.get("prompt_index", 0)

    # Save current response
    field_name = f"response_{prompt_index}"
    await state.update_data({field_name: message.text})

    # Move to the next prompt or finish
    if prompt_index + 1 < len(text_prompts):
        next_prompt = text_prompts[prompt_index + 1]
        await message.answer(next_prompt)
        await state.update_data(prompt_index=prompt_index + 1)
    else:
        # Data collection completed
        user_data = await state.get_data()
        await message.answer("Ma'lumotlar muvaffaqiyatli qabul qilindi!\n\nTekshirib kerakli tugmani bosing:",
                             reply_markup=check_dkb)

        text = (f"<b>Xodim kerak</b>\n\n"
                f"🏢 <b>Idora:</b> {user_data['response_0']}\n"
                f"📚 <b>Texnologiya:</b> {user_data['response_1']}\n"
                f"🔗 <b>Telegram:</b> @{message.from_user.username}\n"
                f"📞 <b>Aloqa:</b> {user_data['response_2']}\n"
                f"🌐 <b>Hudud:</b> {user_data['response_3']}\n"
                f"✍️ <b>Mas'ul:</b> {user_data['response_4']}\n"
                f"🕰 <b>Murojaat qilish vaqti:</b> {user_data['response_5']}\n"
                f"🕰 <b>Ish vaqti:</b> {user_data['response_6']}\n"
                f"💰 <b>Maosh:</b> {user_data['response_7']}\n"
                f"‼️ <b>Qo'shimcha ma'lumotlar:</b> {user_data['response_8']}")
        await message.answer(text=text)
        await state.set_state(NeedWorkerStates.check)


@router.message(NeedWorkerStates.check)
async def confirm_or_reenter_data(message: types.Message, state: FSMContext):
    if message.text == "✅ Tasdiqlash":
        data = await state.get_data()
        user_id = (await db.add_user(telegram_id=message.from_user.id))['id']
        await db.add_user_datas(user_id=user_id, full_name=message.from_user.full_name,
                                username=f'@{message.from_user.username}', age=None, phone=data['response_2'])
        technology_ids = [
            (await db.add_entry(table="technologies", field="technology_name", value=tech.strip()))['id']
            for tech in data['response_1'].split(",")
        ]
        await db.add_technologies(user_id=user_id, technology_ids=technology_ids)
        region_id = (await db.add_entry(table="regions", field="region_name", value=data['response_3']))['id']
        idora_id = (
            await db.add_idoralar(idora_nomi=data['response_0'], masul=data['response_4'], qoshimcha=data['response_8'],
                                  region_id=region_id))['id']
        work_id = (await db.add_srch_worker(idora_id=idora_id, m_vaqti=data['response_5'], i_vaqti=data['response_6'],
                                            maosh=data['response_7']))['id']

        await message.answer(
            f"Ma'lumotlaringiz adminga yuborildi!\n\nSo'rov raqami: {message.from_user.id}{work_id}"
            f"\n\nAdmin tekshirib chiqqanidan so'ng natija yuboriladi!",
            reply_markup=main_dkb())

        # await bot.send_message(ADMIN_GROUP, f"Ish joyi kerak bo'limiga yangi habar qabul qilindi!\n\n"
        #                                     f"{await format_user_data(data, message.from_user.username)}",
        #                        reply_markup=first_check_ikb(telegram_id=telegram_id, row_id=job_id,
        #                                                     department="Ish joyi kerak"))
        await state.clear()
