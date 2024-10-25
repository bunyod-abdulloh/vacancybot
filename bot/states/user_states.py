from aiogram.filters.state import StatesGroup, State


class UserAnketa(StatesGroup):
    fullname = State()
    technology = State()
    phone = State()
    region = State()
    cost = State()
    profession = State()
    apply_time = State()
    maqsad = State()
