from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.handlers.functions.functions_one import failed_message, warning_message, send_to_admin
from bot.keyboards.reply.main_dkb import main_dkb
from bot.keyboards.reply.users_dkb import check_dkb
from loader import db

router = Router()


# State class for apprentice request stages
class ApprenticeRequest(StatesGroup):
    collecting_data = State()
    check = State()


# Questions list for data collection
questions = [
    "👤 Ism sharifingizni kiriting:\n\n<b>Namuna: Birnarsa Birnarsayev</b>",
    "🕑 Yoshingizni kiriting:\n\n<b>Namuna: 20</b>",
    "<b>🧑‍💻 Texnologiya</b>\n\nO'rgatmoqchi bo'lgan texnologiyalaringizni kiriting (vergul bilan ajrating).\n\n<b>Namuna: Java, Python, C++</b>",
    "📞 <b>Aloqa</b>:\n\nTelefon raqamingizni kiriting\n\n<b>Namuna: +998971234567</b>",
    "🌎 Hududingizni kiriting (viloyat/shahar yoki davlat/shahar nomi)\n\n<b>Namuna: Farg'ona, Qo'qon yoki Turkiya, Istanbul</b>",
    "💰 <b>Narxi:</b>\n\nPullik bo'lsa narxni yozing, amaliyot/tajriba uchun bo'lsa bittasini yozing:",
    "👨🏻‍💻 <b>Kasbi:</b>\n\nO'qisangiz talaba/o'quvchi, ishlasangiz lavozim/darajangizni kiriting:\n\n<b>Namuna: Python Developer, Senior</b>",
    "🕰 <b>Murojaat qilish vaqti:</b>\n\nMurojaat qilish vaqtini kiriting:\n\n<b>Namuna: 09:00 - 21:00</b>",
    "📌 <b>Maqsad:</b>\n\nMaqsadingizni yozing"
]


async def format_apprentice_data(data: dict, message: types.Message, to_user=False, to_admin=False,
                                 row_id=None):
    techs = " ".join(f"#{tech.strip().lower()}" for tech in data['apprentice_2'].split(","))
    region = data['apprentice_4'].split(",")[0].split(" ")[0]
    summary = (f"<b>Shogird kerak\n\n</b>"
               f"🎓 <b>Ustoz:</b> {data['apprentice_0']}\n"
               f"🛂 <b>Yosh:</b> {data['apprentice_1']}\n"
               f"📚 <b>Texnologiya:</b> {data['apprentice_2']}\n"
               f"🔗 <b>Telegram:</b> @{message.from_user.username}\n"
               f"📞 <b>Aloqa:</b> {data['apprentice_3']}\n"
               f"🌆 <b>Hudud:</b> {data['apprentice_4']}\n"
               f"💰 <b>Narxi:</b> {data['apprentice_5']}\n"
               f"👨🏻‍💻 <b>Kasbi:</b> {data['apprentice_6']}\n"
               f"🕰 <b>Murojaat qilish vaqti:</b> {data['apprentice_7']}\n"
               f"📌 <b>Maqsad:</b> {data['apprentice_8']}\n\n"
               f"#shogird {techs} #{region}")
    if to_user:
        await message.answer(text=summary)
    if to_admin:
        await send_to_admin(chapter="Sherik kerak", row_id=row_id, telegram_id=message.from_user.id, summary=summary,
                            department="need_apprentice")


# Handler to start data collection
@router.message(F.text == "Shogird kerak")
async def apprentice_needed_main(message: types.Message, state: FSMContext):
    await state.update_data(index=0)  # Initialize index at 0
    await message.answer(questions[0])
    await state.set_state(ApprenticeRequest.collecting_data)


# Handler to collect each data step-by-step
@router.message(ApprenticeRequest.collecting_data)
async def collect_apprentice_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    index = data["index"]

    # Example validation for age
    if index == 1 and not (message.text.isdigit() and len(message.text) == 2):
        await message.answer("Namunada ko'rsatilganidek ikki honali son kiriting!")
        return

    # Save the response and increment the index
    await state.update_data({f"apprentice_{index}": message.text, "index": index + 1})

    # Move to the next question or display summary for confirmation
    if index + 1 < len(questions):
        await message.answer(questions[index + 1])
    else:
        # Prepare the collected data for confirmation
        collected_data = await state.get_data()
        await format_apprentice_data(data=collected_data, message=message, to_user=True)
        await message.answer(f"Kiritilgan ma'lumotlarni tekshirib kerakli tugmani bosing", reply_markup=check_dkb)
        await state.set_state(ApprenticeRequest.check)


# Handler for final confirmation or re-entry
@router.message(ApprenticeRequest.check)
async def apprentice_request_check(message: types.Message, state: FSMContext):
    if message.text == "♻️ Qayta kiritish":
        await apprentice_needed_main(message, state)
    elif message.text == "✅ Tasdiqlash":
        try:
            data = await state.get_data()
            user_id = (await db.add_user(telegram_id=message.from_user.id))['id']
            await db.add_user_datas(user_id=user_id, full_name=data['apprentice_0'],
                                    username=f'@{message.from_user.username}', age=data['apprentice_1'],
                                    phone=data['apprentice_3'])

            region_id = (await db.add_entry("regions", "region_name", data['apprentice_4']))['id']
            profession_id = (await db.add_entry("professions", "profession_name", data['apprentice_6']))['id']
            id_ = (
                await db.add_apprentice(user_id=user_id, profession_id=profession_id,
                                        apply_time=data['apprentice_7'],
                                        cost=data['apprentice_5'], maqsad=data['apprentice_8'], region_id=region_id))[
                'id']

            for tech in data['apprentice_2'].split(","):
                tech_id = (await db.add_entry("technologies", "technology_name", tech.strip()))['id']
                await db.add_technologies(user_id=id_, technology_id=tech_id, table_name="apprentice")
            confirmation_text = (f"Ma'lumotlaringiz adminga yuborildi!\n\n"
                                 f"So'rov raqami: {message.from_user.id}{id_}\n\n"
                                 f"Admin tekshirib chiqqanidan so'ng natija yuboriladi!")
            await format_apprentice_data(data=data, message=message, to_admin=True)
            await message.answer(text=confirmation_text, reply_markup=main_dkb())

            await state.clear()
        except Exception as err:
            await failed_message(message, err)
    else:
        await warning_message(message)
