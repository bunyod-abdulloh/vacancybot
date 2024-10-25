from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.states.user_states import UserAnketa

router = Router()


@router.message(F.text == "Sherik kerak")
async def search_partner_rtr(message: types.Message, state: FSMContext):
    text = ("Hozir Sizga birnecha savollar beriladi\n"
            "Har biriga javob bering.\n"
            "Oxirida agar hammasi to`g`ri bo`lsa, HA tugmasini bosing va arizangiz Adminga yuboriladi.\n\n")

    await message.answer(
        text=f"{text}<b>👤 Ism sharifingizni kiriting:\n\nNamuna: Birnarsa Birnarsayev</b>"
    )
    await state.set_state(
        UserAnketa.fullname
    )


@router.message(UserAnketa.fullname)
async def get_fullname_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        fullname=message.text
    )
    await message.answer(
        text="<b>🧑‍💻 Texnologiya</b>\n\nTalab qilinadigan texnologiyalarni kiriting\n\n"
             "Texnologiya nomlarini vergul bilan ajrating.\n\n<b>Namuna: <i>Java, Python, C++</i></b>"
    )
    await state.set_state(
        UserAnketa.technology
    )


@router.message(UserAnketa.technology)
async def get_technologies_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        technologies=message.text
    )
    await message.answer(
        text="📞 <b>Aloqa</b>: \n\nBog'lanish uchun telefon raqamingizni kiriting\n\n<b><i>Namuna: +998971234567</i></b>"
    )
    await state.set_state(
        UserAnketa.phone
    )


@router.message(UserAnketa.phone)
async def get_phone_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        phone=message.text
    )
    await message.answer(
        text="<b>💰 Narxi:</b>\n\nTo'lov qilasizmi yoki bepulmi? Bepul bo'lsa bepul deb yozing, to'lov qiladigan "
             "bo'lsangiz summani kiriting <b><i>Namuna: 1.200.000 so'm yoki $</i></b>"
    )
    await state.set_state(
        UserAnketa.cost
    )


@router.message(UserAnketa.cost)
async def get_cost_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        cost=message.text
    )
    await message.answer(
        text="👨🏻‍💻 <b>Kasbi:</b>\n\nIshlaysizmi yoki o'qiysizmi?\n\n"
             "<b><i>Namuna: O'qiyman, Talab | Ishlayman, CEO</i></b>"
    )
    await state.set_state(
        UserAnketa.profession
    )


@router.message(UserAnketa.profession)
async def get_profession_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        apply_time=message.text
    )
    await message.answer(
        text="🕰 <b>Murojaat qilish vaqti:</b>\n\nQaysi vaqt oralig'ida murojaat qilish mumkin?\n\n"
             "<b><i>Namuna: 09:00 - 21:00</i></b>"
    )
    await state.set_state(
        UserAnketa.apply_time
    )


@router.message(UserAnketa.apply_time)
async def get_apply_time_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        apply_time=message.text
    )
    await message.answer(
        text="<b>📌 Maqsad:</b>\n\nMaqsadingizni qisqacha yozing"
    )
    await state.set_state(
        UserAnketa.maqsad
    )


@router.message(UserAnketa.maqsad)
async def get_maqsad_rtr(message: types.Message, state: FSMContext):
    data = await state.get_data()
    techs = data['technology'].split(",")
    techs_ = str()
    for tech in techs:
        techs_ += f"#{tech} "
    region = data['region'].split(" ")
    text = (f"<b>👤 Sherik:</b> {data['fullname']}\n"
            f"<b>🧑‍💻 Texnologiya:</b> {data['technology']}\n"
            f"<b>🔗 Telegram: {message.from_user.username}</b>\n"
            f"<b>📞 Aloqa</b> {data}\n"
            f"<b>Hudud:</b>\n"
            f"<b>Narx:</b>\n"
            f"<b>Kasbi:</b>\n"
            f"<b>Murojaat qilish vaqti:</b>"
            f"<b>Maqsad:</b>\n\n"
            f"#sherik {techs_} #{region[0]}")


tech = "Java,Python,Ruby"

split_tech = tech.split(",")
print(split_tech)
