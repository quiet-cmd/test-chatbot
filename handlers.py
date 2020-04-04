from main import bot, dp, types
import apiai
import json
from config import TOKEN_DF, NAME_BOT, database_name
from SQLighter import SQLighter
import random
from aiogram.types import Message, CallbackQuery


# кнопки - название таблиц бд
@dp.message_handler(commands='test')
async def keyboards_start(message: Message):
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
        wrong_answer = str(db_work.select_wrong_answers(table_name, i)[0])
        answer = wrong_answer.split(';')
        answer.append(right_answer)
        random.shuffle(answer)
        row_btn = (types.InlineKeyboardButton(text, callback_data=text) for text in answer)
        keyboard.row(*row_btn)
        await call.message.answer(text=str(db_work.select_question(table_name, i)[0]), reply_markup=keyboard)


# наш DialogFlow
@dp.message_handler()
async def echo(message: Message):
    request = apiai.ApiAI(TOKEN_DF).text_request()
    request.lang = "ru"
    request.session_id = NAME_BOT
    request.query = message.text
    response_json = json.loads(request.getresponse().read().decode("utf-8"))
    response = response_json["result"]["fulfillment"]["speech"]
    await message.answer(text=response)
