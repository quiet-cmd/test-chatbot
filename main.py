import asyncio
from aiogram import Bot, Dispatcher, executor, types, md
from aiogram.types import Message, CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
from config import TOKEN_DF, NAME_BOT, database_name, TOKEN_TG
from SQLighter import SQLighter
import random
import json
import apiai

loop = asyncio.get_event_loop()
bot = Bot(TOKEN_TG, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)

test_cb = CallbackData('post', 'data', 'action', 'index')

user_answers = dict()


def result(db_work, table_name):
    number_of_correct_answers = 0
    for key in range(1, db_work.count_rows(table_name) + 1):
        if user_answers.get(key) == db_work.select_right_answer(table_name, key):
            number_of_correct_answers += 1
    return number_of_correct_answers


@dp.message_handler(commands='start')
async def start(message: types.Message):
    keyboards_for_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns_text = ('/test', '/HELP_ME')
    keyboards_for_start.row(*(types.KeyboardButton(text) for text in btns_text))
    await message.answer("Фростморн жаждет тестов", reply_markup=keyboards_for_start)


@dp.message_handler(commands='test')
async def test_name(message: Message):
    user_answers.clear()
    keyboard_test_name = types.InlineKeyboardMarkup()
    data = SQLighter(database_name).all_table_name()
    text = [i.replace('_', ' ') for i in data]
    text_and_data = zip(text, data)
    row_btn = (types.InlineKeyboardButton(text, callback_data=test_cb.new(data=data, action='test', index=1)) for
               text, data in
               text_and_data)
    keyboard_test_name.row(*row_btn)
    await message.answer(text="Выберите тест", reply_markup=keyboard_test_name)


@dp.callback_query_handler(test_cb.filter(action=['test', 'step+', 'step-']))
async def testing_users(query: types.CallbackQuery, callback_data: dict):
    index = int(callback_data['index'])
    db_work = SQLighter(database_name)
    table_name = callback_data['data']

    if callback_data['action'] == 'step+':
        if index < db_work.count_rows(table_name):
            index += 1
        else:
            await query.answer(text=f'Правильных ответ дано {result(db_work, table_name)}')

    if callback_data['action'] == 'step-':
        if index > 1:
            index -= 1
        else:
            await query.answer(text='У нас нет нулевого вопроса')
            index += 1

    text = md.text(
        md.hbold(f'Вопрос {index} из {db_work.count_rows(table_name)}'),
        md.quote_html(db_work.select_question(table_name, index)),
        '',
        sep='\n')

    right_answer = db_work.select_right_answer(table_name, index)

    answer = db_work.select_wrong_answers(table_name, index).split(';')
    answer.append(right_answer)
    random.shuffle(answer)

    markup = types.InlineKeyboardMarkup()
    row_btn = (types.InlineKeyboardButton(text=text, callback_data=test_cb.new(data=text, action='answer', index=index))
               for
               text in
               answer)
    markup.row(*row_btn)

    markup.add(
        types.InlineKeyboardButton('Следующий',
                                   callback_data=test_cb.new(data=table_name, action='step+', index=index)),
        types.InlineKeyboardButton('предыдущий',
                                   callback_data=test_cb.new(data=table_name, action='step-', index=index)))

    await query.message.edit_text(text=text, reply_markup=markup)


@dp.callback_query_handler(test_cb.filter(action=['answer']))
async def testing_users(query: types.CallbackQuery, callback_data: dict):
    print(callback_data)
    user_answers[callback_data['index']] = callback_data['data']
    print(user_answers)
    await query.answer(text=f'Вы выбрали ответ {callback_data["data"]}')


@dp.message_handler()
async def message_reply(message: Message):
    request = apiai.ApiAI(TOKEN_DF).text_request()
    request.lang = 'ru'
    request.session_id = NAME_BOT
    request.query = message.text
    response_json = json.loads(request.getresponse().read().decode('utf-8'))
    response = response_json['result']['fulfillment']['speech']
    if response:
        await message.answer(text=response)
    else:
        await message.answer('Я вас не понимаю')


if __name__ == '__main__':
    executor.start_polling(dp)
