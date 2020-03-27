from main import bot, dp
from aiogram.types import Message
import apiai
import json
from config import TOKEN_DF, NAME_BOT, admin_id, database_name
from SQLighter import SQLighter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


async def send_to_admin(*args):
    await bot.send_message(chat_id=admin_id, text="Фростморн жаждет крови!")


# кнопки - название таблиц бд
@dp.message_handler(commands='test')
async def keyboards(message: Message):
    text = "Выберите тест"
    name = SQLighter(database_name).all_table_name()
    keyboard = InlineKeyboardMarkup(text=name, callback=list(range(len(name))))
    await message.answer(text=text, reply_markup=keyboard)


@dp.message_handler(commands='start')
async def start_cmd_handler(message: Message):
    keyboard_markup = InlineKeyboardMarkup(row_width=2)
    text = SQLighter(database_name).all_table_name()
    data = list(range(len(text)))
    keyboard_markup.row(*(InlineKeyboardButton(text, callback_data=data) for text, data in zip(text, data)))
    await message.reply("Выберите тест", reply_markup=keyboard_markup)


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
