import asyncio
from aiogram import Bot, Dispatcher, executor, types, md
from aiogram.types import Message
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
from config import TOKEN_DF, NAME_BOT, TOKEN_TG
from storage import sql_data
import random
import apiai
import json

loop = asyncio.get_event_loop()
bot = Bot(TOKEN_TG, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)

genre_selection_cb = CallbackData('post', 'genre', 'action')
user_testing_cb = CallbackData('post', 'test_name', 'genre', 'index', 'action')
answer_cb = CallbackData('post', 'message_id', 'answer', 'right_or_wrong', 'index', 'action')
result_cb = CallbackData('post', 'test_name', 'genre', 'message_id', 'action')


@dp.message_handler(commands='start')
async def start(message: types.Message):
    keyboards_for_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns_text = ('/test', '/help')
    keyboards_for_start.row(*(types.KeyboardButton(text) for text in btns_text))
    await message.answer("Фростморн жаждет тестов", reply_markup=keyboards_for_start)


@dp.message_handler(commands='help')
async def help(message: types.Message):
    s = f'{NAME_BOT} - бот предназначенный для общения и тестирования. Предоставляет справочные материалы на основе \
    неверных ответов пользователя.\nИмеющиеся команды:\n/test - вызов теста'
    await message.answer(s)


@dp.message_handler(commands='test')
async def genre_selection(message: Message):
    keyboard_genres_name = types.InlineKeyboardMarkup()
    genres = sql_data.keys()

    for genre in genres:
        btn = types.InlineKeyboardButton(genre, callback_data=genre_selection_cb.new(genre, 'genres'))
        keyboard_genres_name.row(btn)

    await message.answer("Выберите тест", reply_markup=keyboard_genres_name)


@dp.callback_query_handler(genre_selection_cb.filter(action='genres'))
async def test_selection(query: types.CallbackQuery, callback_data: dict):
    keyboard_tests_name = types.InlineKeyboardMarkup()
    genre = callback_data['genre']
    tests_name = sql_data[genre].keys()

    for test_name in tests_name:
        btn = types.InlineKeyboardButton(test_name, callback_data=user_testing_cb.new(test_name, genre, '0', 'test'))
        keyboard_tests_name.row(btn)

    await query.message.edit_text(text="Выберите тест", reply_markup=keyboard_tests_name)


@dp.callback_query_handler(user_testing_cb.filter(action=['test', 'step+', 'step-']))
async def user_testing(query: types.CallbackQuery, callback_data: dict):
    genre = callback_data['genre']
    test_name = callback_data['test_name']
    test_data = sql_data[genre][test_name]
    index = int(callback_data['index'])
    message_id = str(query.message.message_id)

    if callback_data['action'] == 'step+':
        if index < len(test_data) - 1:
            index += 1
        else:
            await query.answer('Нажмите кнопку "Показать результат"')
    if callback_data['action'] == 'step-':
        if index > 0:
            index -= 1
        else:
            await query.answer('У нас нет нулевого вопроса')

    text = md.text(
        md.hbold(f"Вопрос {test_data[index]['id']} из {test_data[-1]['id']}"),
        md.quote_html(test_data[index]['question']),
        sep='\n')

    correct_answer = test_data[index]['correct_answer']

    answer = test_data[index]['wrong_answers'].split(';')
    answer.append(correct_answer)
    random.shuffle(answer)
    answer_for_btn = {i: 1 if i == correct_answer else 0 for i in answer}

    markup = types.InlineKeyboardMarkup()

    row_btn = (types.InlineKeyboardButton(text,
                                          callback_data=answer_cb.new(message_id, text, data, str(index), 'answer')) for
               text, data in answer_for_btn.items())
    markup.row(*row_btn)

    markup.add(
        types.InlineKeyboardButton('предыдущий', callback_data=user_testing_cb.new(test_name, genre, index, 'step-')),
        types.InlineKeyboardButton('Следующий', callback_data=user_testing_cb.new(test_name, genre, index, 'step+')))
    markup.add(
        types.InlineKeyboardButton('Показать результат',
                                   callback_data=result_cb.new(test_name, genre, message_id, 'result')))
    await query.message.edit_text(text=text, reply_markup=markup)


@dp.callback_query_handler(answer_cb.filter(action=['answer']))
async def testing_users(query: types.CallbackQuery, callback_data: dict):
    message_id = callback_data['message_id']
    index = int(callback_data['index'])
    right_or_wrong = int(callback_data['right_or_wrong'])
    if message_id not in globals():
        globals()[message_id] = dict()
        globals()[message_id][index] = right_or_wrong
    else:
        globals()[message_id][index] = right_or_wrong
    await query.answer(text=f'Вы выбрали ответ {callback_data["answer"]}')


@dp.callback_query_handler(result_cb.filter(action=['result']))
async def result_test(query: types.CallbackQuery, callback_data: dict):
    genre = callback_data['genre']
    test_name = callback_data['test_name']
    test_data = sql_data[genre][test_name]
    message_id = callback_data['message_id']
    num_of_right_answer = 0
    number_of_questions = test_data[-1]['id']
    advice = []

    if message_id not in globals():
        await query.message.edit_text(text='де відповіді?', disable_web_page_preview=True)

    for index, data in globals()[message_id].items():
        num_of_right_answer += data
        if not data:
            advice.append(test_data[index]['advice'])

    del globals()[message_id]

    if not advice:
        text = md.text(
            md.hbold(f'Поздравляю вы прошли тест! Правильных ответов: {num_of_right_answer} из {number_of_questions}'),
            '',
            md.quote_html('Все ваши ответы были правильными, мы открываем книгу секретов лишь нуждающимся'),
            sep='\n'
        )
    else:
        text = md.text(
            md.hbold(f'Поздравляю вы прошли тест! Правильных ответов: {num_of_right_answer} из {number_of_questions}'),
            '',
            md.quote_html('Возможно вам стоит посмотреть следующие материалы:'),
            '',
            md.hitalic(*advice, sep='\n'),
            sep='\n'
        )
    await query.message.edit_text(text=text, disable_web_page_preview=True)


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
