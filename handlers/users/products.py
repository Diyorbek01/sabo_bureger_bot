import urllib.request

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InputFile

from handlers.users.start import check_photo
from keyboards.default.contact_button import keyboard as contact_keyboard
from keyboards.default.menus import keyboard as main_menu_keyboard, product_category
from data.config import BASE_URL, BASE_PHOTO_URL
from keyboards.inline.products import rates, poll_offer
from loader import dp, bot

data = {
    "rate": None,
    "product_id": None,
    "offer_text": None,
    "user_id": None,
}


@dp.message_handler(text="🍴Mahsulotlar", state=["rating_deliverer", "send_offer_deliverer", "get_category"
                                                                                            "rating_product",
                                                "offer", "rating_staff", "send_offer", None])
async def get_offer_products_category(message: types.Message, state: FSMContext):
    res = check_photo()
    if res[0]['product'] is not None:
        urllib.request.urlretrieve(res[0]['product'], "photos/product-image.jpg")
        photo_file = InputFile(path_or_bytesio="photos/product-image.jpg")
        await bot.send_photo(message.from_user.id, photo=photo_file)
    await message.answer("Kerakli bo'limni tanlang", reply_markup=product_category())
    await state.set_state("get_category")


@dp.message_handler(state=['get_category', "rating_product"])
async def get_offer_products(message: types.Message, state: FSMContext):
    category_name = message.text
    url = f"{BASE_URL}/product-category/get_products/?category_name={category_name}"
    response = requests.request("GET", url)
    products = response.json()
    if products == []:
        await bot.send_message(message.from_user.id, "Mahsulotlar mavjud emas")
    else:
        for product in products:
            if product['image'] is not None:
                image = f'{BASE_PHOTO_URL}{product["image"]}'
                urllib.request.urlretrieve(image, "photos/product-image.jpg")
                photo_file = InputFile(path_or_bytesio="photos/product-image.jpg")
                await bot.send_photo(chat_id=message.from_user.id, photo=photo_file, caption=product['name'],
                                     reply_markup=rates(product['id']))
            else:
                await bot.send_message(message.from_user.id, product['name'],
                                       reply_markup=rates(product['id']))
        await state.set_state("rating_product")


@dp.callback_query_handler(state=['rating_product'])
async def inline_last_step_callback_handler(query: types.CallbackQuery, state: FSMContext):
    message = query.data
    rate = message.split('-')[0]
    product_id = message.split('-')[1]
    data['rate'] = rate
    data['product_id'] = product_id
    data['user_id'] = query.from_user.id
    await query.message.delete()
    await query.message.answer("Taklifingizni yozib qoldiring...")
    await state.set_state("offer")


@dp.message_handler(state=["offer"])
async def get_offer_text(message: types.Message, state: FSMContext):
    text = message.text
    data['offer_text'] = text

    url = f"{BASE_URL}/offer/post/"
    response = requests.request("POST", url, data=data)
    if int(response.status_code) == 201:
        status_poll = check_poll(data['product_id'])
        if status_poll != []:
            await message.answer("Ovoz berish jarayonida qatnashasizmi?",
                                 reply_markup=poll_offer(f"product-{data['product_id']}"))
            await state.set_state("poll")
        else:
            await message.answer('Taklifingiz uchun rahmat!')
            await state.set_state('get_category')
    else:
        await message.answer("Xatolik mavjud")
    data.clear()


def check_poll(product_id):
    url = f"{BASE_URL}/poll/get/?product_id={product_id}"
    response = requests.request("GET", url)
    polls = response.json()
    return polls
