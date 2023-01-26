import urllib.request

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InputFile

from keyboards.default.contact_button import keyboard as contact_keyboard
from keyboards.default.menus import keyboard as main_menu_keyboard, product_category
from data.config import BASE_URL, BASE_PHOTO_URL
from keyboards.default.staffs import keyboard
from keyboards.inline.products import rates, poll_offer_staff
from loader import dp, bot

data = {
    "rate": None,
    "offer_text": None,
    "user_id": None,
    "user": None
}


@dp.message_handler(text="🚖Yetkazib beruvchilar", state=["rating_deliverer", "send_offer_deliverer", "get_category"
                                                                                                     "rating_product",
                                                         "offer", "rating_staff", "send_offer", None])
async def get_offer_deliverer(message: types.Message, state: FSMContext):
    url = f"{BASE_URL}/staff/get_deliverer/"
    response = requests.request("GET", url)
    staffs = response.json()
    if staffs == []:
        await bot.send_message(message.from_user.id, "Hodimlar mavjud emas")
    else:
        for staff in staffs:
            text = f"FIO: {staff['full_name']}\n" \
                   f"Mashina rusumi: {staff['car_brand']}\n" \
                   f"Mashina rangi: {staff['car_color']}\n" \
                   f"Mashina raqami: {staff['car_number']}\n" \
                   f" ------------\n" \
                   f"Baholash uchun raqamlardan birini tanlang."
            if staff['avatar'] is not None:
                image = BASE_PHOTO_URL+staff["avatar"]
                urllib.request.urlretrieve(image, "photos/avatar-image.jpg")
                photo_file = InputFile(path_or_bytesio="photos/avatar-image.jpg")
                await bot.send_photo(chat_id=message.from_user.id, photo=photo_file,
                                     caption=text,
                                     reply_markup=rates(staff['id']), parse_mode='HTML')
            else:
                await bot.send_message(message.from_user.id, text,
                                   reply_markup=rates(staff['id']))
            await state.set_state("rating_deliverer")

    @dp.callback_query_handler(state=['rating_deliverer'])
    async def inline_last_step_callback_handler(query: types.CallbackQuery, state: FSMContext):
        message = query.data
        rate = message.split('-')[0]
        user_id = message.split('-')[1]
        data['rate'] = rate
        data['user'] = user_id
        data['user_id'] = query.from_user.id
        await query.message.delete()
        await query.message.answer("Taklifingizni yozib qoldiring...")
        await state.set_state("send_offer_deliverer")

    @dp.message_handler(state=["send_offer_deliverer"])
    async def get_offer_text(message: types.Message, state: FSMContext):
        text = message.text
        data['offer_text'] = text

        url = f"{BASE_URL}/offer/post/"
        response = requests.request("POST", url, data=data)
        if int(response.status_code) == 201:
            status_poll = check_poll(data['user'])
            if status_poll != []:
                await message.answer("Ovoz berish jarayonida qatnashasizmi?",
                                     reply_markup=poll_offer_staff(f"deliverer-{data['user']}"))
                await state.set_state("poll")
            else:
                await message.answer('Taklifingiz uchun rahmat!')
        else:
            await message.answer("Xatolik mavjud")
        data.clear()

    def check_poll(user_id):
        url = f"{BASE_URL}/poll/get_deliverer/?user_id={user_id}"
        response = requests.request("GET", url)
        polls = response.json()
        return polls

