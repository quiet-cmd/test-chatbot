from main import bot, dp
from aiogram.types import Message
from config import admin_id
import apiai
import json
from config import TOKEN_DF, NAME_BOT, database_name
from SQLighter import *
from keyboards import ListOfButtons


async def send_to_admin(*args):
    await bot.send_message(chat_id=admin_id, text="Фростморн жаждет крови!")


# кнопки - название таблиц бд
@dp.message_handler(commands='test')
async def keyboards(message: Message):
    text = "Выберите тест"
    name = SQLighter(database_name).all_table_name()
    keyboard = ListOfButtons(text=name, callback=list(range(len(name)))).inline_keyboard
    await message.answer(text=text, reply_markup=keyboard)


# наш DialogFlow
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
        await message.answer(text="Я не знаю что вам ответить")
