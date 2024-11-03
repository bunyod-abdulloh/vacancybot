from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline.admin_ikb import admin_check_ikb
from bot.keyboards.reply.users_dkb import check_dkb
from bot.states.user_states import LookingPartner
from data.config import BIG_ADMIN
from loader import bot, db

router = Router()


async def ask_for_fullname(message: types.Message, state: FSMContext):
    await message.answer(text="👤 Ism sharifingizni kiriting:\n\n<b>Namuna: Birnarsa Birnarsayev</b>")
    await state.set_state(LookingPartner.fullname)


async def partner_datas(message: types.Message, state: FSMContext, save_to_db: bool = False):
    data = await state.get_data()
    techs = data['technologies'].split(",")
    techs_ = str()
    for tech in techs:
        techs_ += f" #{tech.lstrip().lower()}"
    region = data['region'].split(" ")
    if save_to_db:
        return data
    else:
        text = (f"👤 <b>Sherik:</b> {data['fullname']}\n"
                f"🧑‍💻 <b>Texnologiya:</b> {data['technologies']}\n"
                f"🔗 <b>Telegram:</b> @{message.from_user.username}\n"
                f"📞 <b>Aloqa</b> {data['phone']}\n"
                f"🌎 <b>Hudud:</b> {data['region']}\n"
                f"💰 <b>Narx:</b> {data['cost']}\n"
                f"💻 <b>Kasbi:</b> {data['profession']}\n"
                f"⌚️ <b>Murojaat qilish vaqti:</b> {data['apply_time']}\n"
                f"📌 <b>Maqsad:</b> {data['maqsad']}\n\n"
                f"#sherik {techs_} #{region[0]}")
        return text


@router.message(F.text == "Sherik kerak")
async def search_partner_rtr(message: types.Message, state: FSMContext):
    await ask_for_fullname(
        message, state
    )


@router.message(LookingPartner.fullname)
async def get_fullname_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        fullname=message.text
    )
    await message.answer(
        text="<b>🧑‍💻 Texnologiya</b>\n\nTalab qilinadigan texnologiyalarni kiriting (texnologiya nomlarini vergul "
             "bilan ajrating).\n\n<b>Namuna: Java, Python, C++</b>"
    )
    await state.set_state(
        LookingPartner.technology
    )


@router.message(LookingPartner.technology)
async def get_technologies_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        technologies=message.text
    )
    await message.answer(
        text="📞 <b>Aloqa</b>:\n\nBog'lanish uchun telefon raqamingizni kiriting\n\n<b>Namuna: +998971234567</b>"
    )
    await state.set_state(
        LookingPartner.phone
    )


@router.message(LookingPartner.phone)
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
        LookingPartner.region
    )


@router.message(LookingPartner.region)
async def get_region_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        region=message.text
    )
    await message.answer(
        text="💰 <b>Narxi:</b>\n\nTo'lov qilasizmi yoki bepulmi?\n(bepul bo'lsa bepul deb yozing, to'lov qiladigan "
             "bo'lsangiz summani kiriting)<b>\n\nNamuna: 1.200.000 so'm yoki $</b>"
    )
    await state.set_state(
        LookingPartner.cost
    )


@router.message(LookingPartner.cost)
async def get_cost_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        cost=message.text
    )
    await message.answer(
        text="👨🏻‍💻 <b>Kasbi:</b>\n\nIshlaysizmi yoki o'qiysizmi?\n\n"
             "<b>Namuna: O'qiyman, Talaba | Ishlayman, CEO</b>"
    )
    await state.set_state(
        LookingPartner.profession
    )


@router.message(LookingPartner.profession)
async def get_profession_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        profession=message.text
    )
    await message.answer(
        text="🕰 <b>Murojaat qilish vaqti:</b>\n\nQaysi vaqt oralig'ida murojaat qilish mumkin?\n\n"
             "<b>Namuna: 09:00 - 21:00</b>"
    )
    await state.set_state(
        LookingPartner.apply_time
    )


@router.message(LookingPartner.apply_time)
async def get_apply_time_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        apply_time=message.text
    )
    await message.answer(
        text="📌 <b>Maqsad:</b>\n\nMaqsadingizni qisqacha yozing"
    )
    await state.set_state(
        LookingPartner.maqsad
    )


@router.message(LookingPartner.maqsad)
async def get_maqsad_rtr(message: types.Message, state: FSMContext):
    await state.update_data(
        maqsad=message.text
    )
    datas = await partner_datas(
        message, state
    )
    await message.answer(
        text=datas
    )
    await message.answer(
        text="Kiritilgan barcha ma'lumotlarni tekshirib kerakli tugmani bosing", reply_markup=check_dkb
    )
    await state.set_state(LookingPartner.check)


@router.message(LookingPartner.check)
async def partner_check_rtr(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id

    if message.text == "♻️ Qayta kiritish":
        await ask_for_fullname(
            message, state
        )
    elif message.text == "✅ Tasdiqlash":
        save_to_db = await partner_datas(
            message, state, save_to_db=True
        )
        # user_id = int()
        existing_partner = await db.get_user(
            telegram_id=telegram_id
        )

        if existing_partner:
            user_id = existing_partner['id']
        else:
            user = await db.add_user(
                telegram_id=telegram_id, username=f'@{message.from_user.username}',
                full_name=save_to_db['fullname'], phone=save_to_db['phone']
            )
            user_id = user['id']

        datas = await partner_datas(
            message, state
        )

        region = await db.add_entry(
            table="regions", field="region_name", value=save_to_db.get('region')
        )
        profession = await db.add_entry(
            table="professions", field="profession_name", value=save_to_db.get('profession')
        )

        technologies = save_to_db.get('technologies', '').split(",")
        technology_ids = []

        for technology in technologies:
            technology_ = await db.add_entry(
                table="technologies", field="technology_name", value=technology.strip()
            )
            technology_ids.append(technology_['id'])

        await db.add_partner_technologies(
            partner_id=user_id, technology_ids=technology_ids,
        )

        await db.add_srch_partner(
            user_id=user_id, region_id=region['id'], profession_id=profession['id'],
            apply_time=save_to_db['apply_time'], cost=save_to_db['cost'], maqsad=save_to_db['maqsad']
        )
        await bot.send_message(
            chat_id=BIG_ADMIN,
            text=f"Sherik kerak bo'limiga yangi habar qabul qilindi!\n\n{datas}",
            reply_markup=admin_check_ikb(
                user_id=message.from_user.id
            )
        )
        await state.clear()
    else:
        await state.clear()
