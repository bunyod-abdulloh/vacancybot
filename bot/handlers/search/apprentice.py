from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.reply.users_dkb import check_dkb

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
        summary = (
            f"🎓 <b>Ustoz:</b> {collected_data['apprentice_0']}\n"
            f"🛂 <b>Yosh:</b> {collected_data['apprentice_1']}\n"
            f"📚 <b>Texnologiya:</b> {collected_data['apprentice_2']}\n"
            f"🔗 <b>Telegram:</b> @{message.from_user.username}\n"
            f"📞 <b>Aloqa:</b> {collected_data['apprentice_3']}\n"
            f"🌆 <b>Hudud:</b> {collected_data['apprentice_4']}\n"
            f"💰 <b>Narxi:</b> {collected_data['apprentice_5']}\n"
            f"👨🏻‍💻 <b>Kasbi:</b> {collected_data['apprentice_6']}\n"
            f"🕰 <b>Murojaat qilish vaqti:</b> {collected_data['apprentice_7']}\n"
            f"📌 <b>Maqsad:</b> {collected_data['apprentice_8']}"
        )
        await message.answer(f"Kiritilgan ma'lumotlarni tekshiring:\n\n{summary}", reply_markup=check_dkb)
        await state.set_state(ApprenticeRequest.check)


# Handler for final confirmation or re-entry
@router.message(ApprenticeRequest.check)
async def apprentice_request_check(message: types.Message, state: FSMContext):
    if message.text == "♻️ Qayta kiritish":
        await apprentice_needed_main(message, state)
    elif message.text == "✅ Tasdiqlash":
        collected_data = await state.get_data()
        summary = (
            f"🎓 <b>Ustoz:</b> {collected_data['apprentice_0']}\n"
            f"🛂 <b>Yosh:</b> {collected_data['apprentice_1']}\n"
            f"📚 <b>Texnologiya:</b> {collected_data['apprentice_2']}\n"
            f"🔗 <b>Telegram:</b> @{message.from_user.username}\n"
            f"📞 <b>Aloqa:</b> {collected_data['apprentice_3']}\n"
            f"🌆 <b>Hudud:</b> {collected_data['apprentice_4']}\n"
            f"💰 <b>Narxi:</b> {collected_data['apprentice_5']}\n"
            f"👨🏻‍💻 <b>Kasbi:</b> {collected_data['apprentice_6']}\n"
            f"🕰 <b>Murojaat qilish vaqti:</b> {collected_data['apprentice_7']}\n"
            f"📌 <b>Maqsad:</b> {collected_data['apprentice_8']}"
        )
        await message.answer("Ma'lumotlaringiz muvaffaqiyatli yuborildi!")
        await state.clear()
    else:
        await message.answer("Faqat ♻️ Qayta kiritish yoki ✅ Tasdiqlash buyruqlarini kiriting!")
