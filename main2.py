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

posts_cb = CallbackData('post', 'data', 'action', 'index')


def get_keyboard(POSTS) -> types.InlineKeyboardMarkup:
    """
    Generate keyboard with list of posts
    """
    markup = types.InlineKeyboardMarkup(row_width=2)
    for post_id, post in POSTS.items():
        markup.add(
            types.InlineKeyboardButton(
                post['title'],
                callback_data=posts_cb.new(id=post_id, action='view')),
        )
    return markup


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
    row_btn = (types.InlineKeyboardButton(text, callback_data=posts_cb.new(data=data, action='test', index=1)) for
               text, data in
               text_and_data)
    keyboard_test_name.row(*row_btn)
    await message.answer(text="Выберите тест", reply_markup=keyboard_test_name)


@dp.callback_query_handler(posts_cb.filter(action=['test', 'step+', 'step-']))
async def query_show_list(query: types.CallbackQuery, callback_data: dict):
    index = int(callback_data['index'])
    db_work = SQLighter(database_name)
    table_name = callback_data['data']

    if callback_data['action'] == 'step+':
        if index < db_work.count_rows(table_name):
            index += 1
        else:
            await query.answer(text='Тут будет результат теста')
    if callback_data['action'] == 'step-':
        if index > 1:
            index -= 1
        else:
            await query.answer(text='У нас нет нулевого вопроса')

    text = md.text(
        md.hbold(f"Вопрос {index} из {db_work.count_rows(table_name)}"),
        md.quote_html(db_work.select_question(table_name, index)),
        '',
        sep='\n')

    right_answer = db_work.select_right_answer(table_name, index)

    answer = db_work.select_wrong_answers(table_name, index).split(';')
    answer.append(right_answer)
    random.shuffle(answer)
    answer = {i: '1' if i == right_answer else '0' for i in answer}

    markup = types.InlineKeyboardMarkup()
    row_btn = (types.InlineKeyboardButton(text=text, callback_data=posts_cb.new(data=text, action=b, index=index)) for
               text, b in
               answer.items())
    markup.row(*row_btn)
    markup.add(
        types.InlineKeyboardButton('Next', callback_data=posts_cb.new(data=table_name, action='step+', index=index)),
        types.InlineKeyboardButton('Back', callback_data=posts_cb.new(data=table_name, action='step-', index=index)))
    await query.message.edit_text(text=text, reply_markup=markup)


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
