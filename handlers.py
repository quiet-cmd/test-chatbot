from main import bot, dp
import apiai
import json
from config import TOKEN_DF, NAME_BOT, database_name
from SQLighter import SQLighter
from keyboards import ListOfButtons
from filters import *


# кнопки - название таблиц бд
@dp.message_handler(commands='test')
async def keyboards_start(message: Message):
    data = SQLighter(database_name).all_table_name()
    text = [i.replace('_', ' ') for i in data]
    keyboard = ListOfButtons(text=text, callback=data).inline_keyboard
    await message.answer(text="Выберите тест", reply_markup=keyboard)


@dp.callback_query_handler(Button("Физкультура_1"))
async def keyboards_test(call: CallbackQuery):
    db_work = SQLighter(database_name)
    table_name = str(call.data)
    print(table_name)
    for i in range(1, db_work.count_rows(table_name) + 1):
        right_answer = db_work.select_right_answer(table_name, i)[0]
        answers = str(db_work.select_wrong_answers(table_name, i)[0]).split(';')
        answers.append(right_answer)
        keyboard = ListOfButtons(text=answers, callback=answers).inline_keyboard
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
