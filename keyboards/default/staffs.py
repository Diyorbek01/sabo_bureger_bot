import requests
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from data.config import BASE_URL

keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                               keyboard=[
                                   [
                                       KeyboardButton(text="Ofitsiantlar")
                                   ],
                                   [
                                       KeyboardButton(text="Boshqaruvchilar")
                                   ],
                                   [
                                       KeyboardButton(text="Kassirlar")
                                   ]
                               ])
