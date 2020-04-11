import asyncio
from aiogram import Bot, Dispatcher, executor, types, md
from aiogram.types import Message
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
from config import TOKEN_DF, NAME_BOT, database_name, TOKEN_TG, storage_name
from SQLighter import SQLighter
import random
import json
import apiai

loop = asyncio.get_event_loop()
bot = Bot(TOKEN_TG, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)

test_cb = CallbackData('post', 'data', 'action', 'index')
answer_cb = CallbackData('post', 'post_id', 'answer', 'right_or_wrong', 'question_number', 'action')
result_cb = CallbackData('post', 'table_name', 'action', 'number_of_questions')


@dp.message_handler(commands='start')
async def start(message: types.Message):
    keyboards_for_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns_text = ('/test', '/HELP_ME')
    keyboards_for_start.row(*(types.KeyboardButton(text) for text in btns_text))
    await message.answer("Фростморн жаждет тестов", reply_markup=keyboards_for_start)


@dp.message_handler(commands='test')
async def test_name(message: Message):
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
    post_id = query.message.message_id
    db_work = SQLighter(database_name)
    table_name = callback_data['data']

    number_of_questions = db_work.count_rows(table_name)

    if callback_data['action'] == 'step+':
        if index < number_of_questions:
            index += 1
        else:
            await query.answer(text=f'Нажмите кнопку "Показать результат"')
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
    answer_for_btn = {i: 1 if i == right_answer else 0 for i in answer}
    markup = types.InlineKeyboardMarkup()
    row_btn = (types.InlineKeyboardButton(text=text,
                                          callback_data=answer_cb.new(post_id=post_id, answer=text, right_or_wrong=data,
                                                                      question_number=index, action='answer')) for
               text, data in answer_for_btn.items())
    markup.row(*row_btn)
    markup.add(
        types.InlineKeyboardButton('Следующий',
                                   callback_data=test_cb.new(data=table_name, action='step+', index=index)),
        types.InlineKeyboardButton('предыдущий',
                                   callback_data=test_cb.new(data=table_name, action='step-', index=index)))
    markup.add(
        types.InlineKeyboardButton('Показать результат',
                                   callback_data=result_cb.new(table_name=table_name, action='result',
                                                               number_of_questions=number_of_questions)))
    await query.message.edit_text(text=text, reply_markup=markup)


@dp.callback_query_handler(answer_cb.filter(action=['answer']))
async def testing_users(query: types.CallbackQuery, callback_data: dict):
    print(callback_data)
    SQLighter(storage_name).insert_row(callback_data['post_id'], callback_data['right_or_wrong'],
                                       callback_data['question_number'])
    await query.answer(text=f'Вы выбрали ответ {callback_data["answer"]}')


@dp.callback_query_handler(result_cb.filter(action=['result']))
async def result_test(query: types.CallbackQuery, callback_data: dict):
    db_work = SQLighter(storage_name)
    num_of_right_answer = db_work.number_of_correct_answers(query.message.message_id)
    db_work.delete_rows(query.message.message_id)

    await query.message.edit_text(
        text=f'Поздравляю вы прошли тест.! Правильных ответов: {num_of_right_answer} из {callback_data["number_of_questions"]}')


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
