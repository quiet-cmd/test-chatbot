import asyncio
from aiogram import Bot, Dispatcher, executor, types, md
from aiogram.types import Message, CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN_DF, NAME_BOT, database_name, TOKEN_TG
from SQLighter import SQLighter
import random
import json
import apiai

import logging
import uuid

from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified, Throttled

loop = asyncio.get_event_loop()
bot = Bot(TOKEN_TG, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)

posts_cb = CallbackData('post', 'data', 'action')


@dp.message_handler(commands='start')
async def start(message: types.Message):
    keyboards_for_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns_text = ('/test', '/')
    keyboards_for_start.row(*(types.KeyboardButton(text) for text in btns_text))
    await message.answer("Фростморн жаждет тестов", reply_markup=keyboards_for_start)


@dp.message_handler(commands='test')
async def test_name(message: Message):
    keyboard_test_name = types.InlineKeyboardMarkup()
    data = SQLighter(database_name).all_table_name()
    text = [i.replace('_', ' ') for i in data]
    text_and_data = zip(text, data)
    row_btn = (types.InlineKeyboardButton(text, callback_data=posts_cb.new(data=data, action='test')) for text, data in
               text_and_data)
    keyboard_test_name.row(*row_btn)
    await message.answer(text="Выберите тест", reply_markup=keyboard_test_name)


@dp.callback_query_handler(posts_cb.filter(action=['test']))
async def query_show_list(query: types.CallbackQuery, callback_data: dict):
    db_work = SQLighter(database_name)
    table_name = callback_data['data']

    POSTS = {
        str(uuid.uuid4()): {
            'question': md.text(
                md.hbold(f"Вопрос {index} из {db_work.count_rows(table_name)}"),
                md.quote_html(db_work.select_question(table_name, index)),
                '',
                sep='\n', ),
            'right_answer': db_work.select_right_answer(table_name, index),
            'wrong_answer': db_work.select_wrong_answers(table_name, index).split(';'),
            'test_name': callback_data['data']
        } for index in range(1, db_work.count_rows(table_name) + 1)
    }

    print(POSTS)
    for post_id, post in POSTS.items():
        print(POSTS[post_id]['question'], POSTS[post_id]['wrong_answer'])


@dp.callback_query_handler(posts_cb.filter(action=['answer']))
async def query_show(query: types.CallbackQuery, callback_data: dict):
    print(callback_data)


@dp.message_handler()
async def message_reply(message: Message):
    request = apiai.ApiAI(TOKEN_DF).text_request()
    request.lang = "ru"
    request.session_id = NAME_BOT
    request.query = message.text
    response_json = json.loads(request.getresponse().read().decode("utf-8"))
    response = response_json["result"]["fulfillment"]["speech"]
    if response:
        await message.answer(text=response)
    else:
        await message.answer('Я вас не понимаю')


if __name__ == '__main__':
    executor.start_polling(dp)
