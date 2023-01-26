from aiogram.dispatcher.filters.state import StatesGroup, State


# Shaxsiy ma'lumotlarni yig'sih uchun PersonalData holatdan yaratamiz
class PersonalData(StatesGroup):
    # Foydalanuvchi buyerda 3 ta holatdan o'tishi kerak
    phoneNum = State()  # Tel raqami


class VotingMenu(StatesGroup):
    # Foydalanuvchi buyerda 3 ta holatdan o'tishi kerak
    products = State()  # email
    staffs = State()  # Tel raqami
    deliverer = State()  # Tel raqami
