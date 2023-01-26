import json
import urllib

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile

from data.config import BASE_URL, BASE_PHOTO_URL
from loader import dp, bot

poll_message_id = {
    "message_id": 0,
    "message": 0,
    "photo_id": 0,
    "photo_message_id": 0,
    "message_instance": None
}
poll_state = {
    "index": -1,
    "length": 0,
    "product_id": 0,
    "status": None
}

variants = []


@dp.callback_query_handler(state=['poll', None])
async def check_poll(query: types.CallbackQuery, state: FSMContext):
    data = query.data
    first_index = data.split('-')[0]
    id = data.split('-')[1]
    if first_index == "cancel":
        await query.message.answer("Taklifingiz  uchun rahmat.")
        if id == "product":
            await state.set_state('get_category')
        else:
            await state.finish()

    elif first_index == "product":
        url = f"{BASE_URL}/poll/get/?product_id={id}"
        poll_state['status'] = 'product'
    elif first_index == "staff":
        url = f"{BASE_URL}/poll/get_staff/?user_id={id}"
        poll_state['status'] = 'staff'
    elif first_index == "deliverer":
        url = f"{BASE_URL}/poll/get_deliverer/?user_id={id}"
        poll_state['status'] = 'deliverer'
    if first_index != "cancel":
        response = requests.request("GET", url)
        polls = response.json()
        if polls != []:
            variants.clear()
            poll_state["index"] = -1
            poll_state["product_id"] = 0
            poll_state["length"] = 0
            poll_state['length'] = len(polls)
            poll_state['product_id'] = id
            poll = polls[poll_state['index'] + 1]
            poll_state['index'] += 1
            if poll['variants'] != []:
                for index_variant, variant in enumerate(poll['variants']):
                    variants.append({
                        'variant': variant,
                        'index_variant': index_variant,
                        'poll_id': poll['id'],
                    })

                if poll['image'] is not None:
                    image = f'{BASE_PHOTO_URL}{poll["image"]}'
                    urllib.request.urlretrieve(image, "photos/poll-image.jpg")
                    photo_file = InputFile(path_or_bytesio="photos/product-image.jpg")
                    photo_id = await query.message.answer_photo(photo=photo_file)
                    poll_message_id["photo_message_id"] = photo_id.message_id
                msg = await query.message.answer_poll(question=poll['question'],
                                                      options=[x['name'] for x in poll['variants']],
                                                      correct_option_id=5, is_anonymous=False)
                poll_message_id['message_id'] = msg.message_id
        else:
            await query.message.answer("So'rovnoma mavjud emas.")
        if poll_state['status'] == 'product':
            await state.set_state('get_category')
        else:
            await state.finish()
    await query.message.delete()


@dp.poll_answer_handler()
async def handle_poll_answer(quiz_answer: types.PollAnswer):
    variant_id = [var['variant']['id'] for var in variants if quiz_answer.option_ids[0] == var['index_variant']][0]
    poll_id = [var['poll_id'] for var in variants if quiz_answer.option_ids[0] == var['index_variant']][0]
    send_poll(variant_id, poll_id, quiz_answer.user.id)
    if poll_message_id['photo_message_id'] != 0:
        try:
            await bot.delete_message(chat_id=quiz_answer.user.id, message_id=poll_message_id['photo_message_id'])
        except:
            if poll_message_id['photo_id'] != 0:
                await bot.delete_message(chat_id=quiz_answer.user.id, message_id=poll_message_id['photo_id'])
            pass
        finally:
            pass

    if poll_state['length'] > poll_state['index'] + 1:
        await send_pol(quiz_answer, poll_state['product_id'])
    else:
        await quiz_answer.bot.send_message(quiz_answer.user.id, "So'rovnomada qatnashganingiz uchun rahmat!")
    try:
        await bot.delete_message(chat_id=quiz_answer.user.id, message_id=poll_message_id['message_id'])
        poll_message_id.pop('message_id')
    except:
        await bot.delete_message(chat_id=quiz_answer.user.id, message_id=poll_message_id['message'])
        poll_message_id.pop('message')


def send_poll(variant, poll_id, user_id):
    url = f"{BASE_URL}/poll-result/post/"
    payload = {
        "poll": poll_id,
        "variant_id": variant,
        "tg_user": user_id,
    }
    response = requests.request("POST", url, data=payload)
    status = response.status_code
    return status


async def send_pol(quiz_answer, product_id):
    if poll_state['status'] == 'product':
        url = f"{BASE_URL}/poll/get/?product_id={product_id}"
    elif poll_state['status'] == 'staff':
        url = f"{BASE_URL}/poll/get_staff/?user_id={product_id}"
    elif poll_state['status'] == 'deliverer':
        url = f"{BASE_URL}/poll/get_deliverer/?user_id={product_id}"

    response = requests.request("GET", url)
    polls = response.json()
    if polls != []:
        variants.clear()
        poll_state['length'] = len(polls)
        poll_state['product_id'] = product_id
        poll = polls[poll_state['index'] + 1]
        poll_state['index'] += 1
        if poll['variants'] != []:
            for index_variant, variant in enumerate(poll['variants']):
                variants.append({
                    'variant': variant,
                    'index_variant': index_variant,
                    'poll_id': poll['id'],
                })

            if poll['image'] is not None:
                image = f'{BASE_PHOTO_URL}{poll["image"]}'
                urllib.request.urlretrieve(image, "photos/poll-image.jpg")
                photo_file = InputFile(path_or_bytesio="photos/product-image.jpg")
                photo_id = await quiz_answer.bot.send_photo(quiz_answer.user.id, photo=photo_file)
                print(photo_id)
                poll_message_id['photo_id'] = photo_id.message_id
                print(poll_message_id['photo_id'])
            msg_id = await quiz_answer.bot.send_poll(quiz_answer.user.id, question=poll['question'],
                                                     options=[x['name'] for x in poll['variants']],
                                                     is_anonymous=False)
            poll_message_id['message'] = msg_id.message_id
    else:
        await quiz_answer.bot.send_message(quiz_answer.user.id, "So'rovnoma mavjud emas.")
