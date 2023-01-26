import requests
from aiogram import types
from aiogram.dispatcher.filters import state
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import BASE_URL


def get_products(category_name):
    url = f"{BASE_URL}/product-category/get_products/?category_name={category_name}"
    response = requests.request("GET", url)
    keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
    for i in response.json():
        keyboard_markup.insert(
            types.InlineKeyboardButton(text=f"{i['name']} | {i['order_count']}", callback_data=f"{i['id']}"),
        )

    return keyboard_markup


def rates(product_id):
    rate = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1", callback_data=f"1-{product_id}"),
                InlineKeyboardButton(text="2", callback_data=f"2-{product_id}"),
                InlineKeyboardButton(text="3", callback_data=f"3-{product_id}"),
                InlineKeyboardButton(text="4", callback_data=f"4-{product_id}"),
                InlineKeyboardButton(text="5", callback_data=f"5-{product_id}"),
            ]
        ])
    return rate


def poll_offer(result):
    rate = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅Ha", callback_data=result),
                InlineKeyboardButton(text="❌Yo'q", callback_data="cancel-product"),
            ]
        ])
    return rate
def poll_offer_staff(result):
    rate = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅Ha", callback_data=result),
                InlineKeyboardButton(text="❌Yo'q", callback_data="cancel-cancel"),
            ]
        ])
    return rate

