from main import bot, dp
from aiogram.types import Message
from config import admin_id
import apiai, json
from config import TOKEN_DF, NAME_BOT


# При запуске бота админ получит сообщение.
async def send_to_admin(*args):
    await bot.send_message(chat_id=admin_id, text="Фростморн жаждет крови!")


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