import requests
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from data.config import BASE_URL

keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                               keyboard=[
                                   [
                                       KeyboardButton(text="🍴Mahsulotlar")
                                   ],
                                   [
                                       KeyboardButton(text="👥Hodimlar")
                                   ],
                                   [
                                       KeyboardButton(text="🚖Yetkazib beruvchilar")
                                   ]
                               ])


def product_category():
    url = f"{BASE_URL}/product-category/"
    response = requests.request("GET", url)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, )
    for i in response.json():
        keyboard.insert(
            KeyboardButton(text=f"{i['name']}"),
        )
    keyboard.insert(
        KeyboardButton(text="Orqaga"),
    )
    return keyboard
