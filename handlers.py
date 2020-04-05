from main import bot, dp
from config import TOKEN_DF, NAME_BOT, database_name
from SQLighter import SQLighter
from aiogram import types
from aiogram.types import Message, CallbackQuery
import random
import json
import apiai


@dp.message_handler(commands='start')
async def start(message: types.Message):
    keyboards_for_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns_text = ('/test', '/')
    keyboards_for_start.row(*(types.KeyboardButton(text) for text in btns_text))
    await message.answer("Фростморн жаждет тестов", reply_markup=keyboards_for_start)


@dp.message_handler(commands='test')
async def keyboards_test_name(message: Message):
    keyboard_test_name = types.InlineKeyboardMarkup()
    data = SQLighter(database_name).all_table_name()
    text = [i.replace('_', ' ') for i in data]
    text_and_data = zip(text, data)
    row_btn = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    keyboard_test_name.row(*row_btn)
    await message.answer(text="Выберите тест", reply_markup=keyboard_test_name)


@dp.callback_query_handler(text=["Физкультура_1", "Физкультура_2"])
async def keyboards_test(call: CallbackQuery):
    db_work = SQLighter(database_name)
    table_name = str(call.data)
    for i in range(1, db_work.count_rows(table_name) + 1):
        keyboard = types.InlineKeyboardMarkup()
        right_answer = db_work.select_right_answer(table_name, i)[0]
        answer = str(db_work.select_wrong_answers(table_name, i)[0]).split(';')
        answer.append(right_answer)
        random.shuffle(answer)
        row_btn = (types.InlineKeyboardButton(text, callback_data=text) for text in answer)
        keyboard.row(*row_btn)
        await call.message.edit_text(text=str(db_work.select_question(table_name, i)[0]), reply_markup=keyboard)


@dp.message_handler()
async def echo(message: Message):
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
