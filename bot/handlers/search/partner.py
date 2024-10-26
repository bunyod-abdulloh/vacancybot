from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.states.user_states import UserAnketa

router = Router()


@router.message(F.text == "Sherik kerak")
async def search_partner_rtr(message: types.Message, state: FSMContext):

    await message.answer(
        text="👤 Ism sharifingizni kiriting:\n\n<b>Namuna: Birnarsa Birnarsayev</b>"
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
        text="<b>🧑‍💻 Texnologiya</b>\n\nTalab qilinadigan texnologiyalarni kiriting (texnologiya nomlarini vergul "
             "bilan ajrating).\n\n<b>Namuna: Java, Python, C++</b>"
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
        text="📞 <b>Aloqa</b>:\n\nBog'lanish uchun telefon raqamingizni kiriting\n\n<b>Namuna: +998971234567</b>"
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
        text="🌎 Hududingiz qaysi?\n\n"
             "(O'zbekistonda bo'lsangiz viloyat yoki shahar nomini, chet elda bo'lsangiz davlat va shahar nomini "
             "kiriting)\n\n"
             "<b>Namuna: Toshkent shahri yoki Turkiya, Istanbul</b>"
    )
    await state.set_state(
        UserAnketa.region
    )


@router.message(UserAnketa.region)
async def get_region_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        region=message.text
    )
    await message.answer(
        text="💰 <b>Narxi:</b>\n\nTo'lov qilasizmi yoki bepulmi?\n(bepul bo'lsa bepul deb yozing, to'lov qiladigan "
             "bo'lsangiz summani kiriting)<b>\n\nNamuna: 1.200.000 so'm yoki $</b>"
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
             "<b>Namuna: O'qiyman, Talaba | Ishlayman, CEO</b>"
    )
    await state.set_state(
        UserAnketa.profession
    )


@router.message(UserAnketa.profession)
async def get_profession_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        profession=message.text
    )
    await message.answer(
        text="🕰 <b>Murojaat qilish vaqti:</b>\n\nQaysi vaqt oralig'ida murojaat qilish mumkin?\n\n"
             "<b>Namuna: 09:00 - 21:00</b>"
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
        text="📌 <b>Maqsad:</b>\n\nMaqsadingizni qisqacha yozing"
    )
    await state.set_state(
        UserAnketa.maqsad
    )


@router.message(UserAnketa.maqsad)
async def get_maqsad_rtr(message: types.Message, state: FSMContext):
    data = await state.get_data()
    techs = data['technologies'].split(",")
    techs_ = str()
    for tech in techs:
        techs_ += f" #{tech.lstrip()}"
    region = data['region'].split(" ")
    text = (f"👤 <b>Sherik:</b> {data['fullname']}\n"
            f"🧑‍💻 <b>Texnologiya:</b> {data['technologies']}\n"
            f"🔗 <b>Telegram:</b> @{message.from_user.username}\n"
            f"📞 <b>Aloqa</b> {data['phone']}\n"
            f"🌎 <b>Hudud:</b> {data['region']}\n"
            f"💰 <b>Narx:</b> {data['cost']}\n"
            f"💻 <b>Kasbi:</b> {data['profession']}\n"
            f"⌚️ <b>Murojaat qilish vaqti:</b> {data['apply_time']}\n"
            f"📌 <b>Maqsad:</b> {message.text}\n\n"
            f"#sherik {techs_} #{region[0]}")
    await message.answer(
        text=text
    )
