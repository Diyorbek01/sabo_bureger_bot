import urllib

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InputFile, Message, ReplyKeyboardRemove

from data.config import BASE_URL
from keyboards.default.contact_button import keyboard as contact_keyboard
from keyboards.default.menus import keyboard as main_menu_keyboard
from loader import dp, bot


def check_photo():
    url = f"{BASE_URL}/photos/"
    response = requests.request("GET", url)
    return response.json()


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    url = f"{BASE_URL}/user/check_user/?tg_id={tg_id}"
    response = requests.request("GET", url)
    status = response.status_code
    res = check_photo()
    if int(status) == 200:
        if res[0]['registration'] is not None:
            urllib.request.urlretrieve(res[0]['registration'], "photos/registration-image.jpg")
            photo_file = InputFile(path_or_bytesio="photos/registration-image.jpg")
            await bot.send_photo(message.from_user.id, photo=photo_file)
        await message.answer("Quyidagi tugmani bosib telefon raqamingizni yuboring",
                             reply_markup=contact_keyboard)
    elif int(status) == 400:
        if res[0]['start'] is not None:
            urllib.request.urlretrieve(res[0]['start'], "photos/start-image.jpg")
            photo_file = InputFile(path_or_bytesio="photos/start-image.jpg")
            await bot.send_photo(message.from_user.id, photo=photo_file)
        await message.answer("Kerakli bo'limni tanlang", reply_markup=main_menu_keyboard)


@dp.message_handler(content_types='contact')
async def get_contact(message: Message):
    contact = message.contact
    url = f"{BASE_URL}/user/"
    payload = {
        "full_name": contact.full_name,
        "phone_number": contact.phone_number,
        "tg_id": contact.user_id,
    }
    response = requests.request("POST", url, data=payload)
    products = response.json()
    await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz",
                         reply_markup=ReplyKeyboardRemove())
    await message.answer("Kerakli bo'limni tanlang", reply_markup=main_menu_keyboard)


@dp.message_handler(text="Orqaga", state=["get_category", "rating_product", "offer", None])
async def back(message: types.Message, state: FSMContext):
    await message.answer("Kerakli bo'limni tanglang", reply_markup=main_menu_keyboard)
    await state.finish()

