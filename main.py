import telebot
from telebot import apihelper
import apiai, json
import constants
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

apihelper.proxy = {"https": constants.PROXY}
bot = telebot.TeleBot(constants.TOKEN_TG)


# Просто стартовое меню
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    user_markup.row_width = 2
    user_markup.add("/test", "/")
    bot.send_message(message.from_user.id, "Здравствуйте", reply_markup=user_markup)


# менюшка с предложением пройти тест
@bot.message_handler(commands=["test"])
def handle_all_test(message):
    test_markup_choice = InlineKeyboardMarkup(row_width=2)
    test_markup_choice.add(InlineKeyboardButton("Yes", callback_data="all_test_yes"),
                           InlineKeyboardButton("No", callback_data="all_test_no"))
    bot.send_message(message.chat.id, "Вы хотите пройти тест?", reply_markup=test_markup_choice)


# если мы ответили что хотим пройти тест
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "all_test_yes":
        bot.answer_callback_query(call.id, "МЫ НЕ ГОТОВЫ")
        all_test_markup = InlineKeyboardMarkup(row_width=1)
        for i in constants.ALL_TEST_NAME:  # кнопки с названием всех тестов
            all_test_markup.add(InlineKeyboardButton(text=i, callback_data=constants.ALL_TEST_NAME[i]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите тест",
                              reply_markup=all_test_markup)
    elif call.data == "all_test_no":
        bot.answer_callback_query(call.id, "ВЫ НЕ ГОТОВЫ")


# наш DialogFlow
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    request = apiai.ApiAI(constants.TOKEN_DF).text_request()
    request.lang = "ru"
    request.session_id = constants.NAME_BOT
    request.query = message.text
    response_json = json.loads(request.getresponse().read().decode("utf-8"))
    response = response_json["result"]["fulfillment"]["speech"]
    if response:
        bot.send_message(message.from_user.id, response)
    else:
        bot.send_message(message.from_user.id, "Я Вас не совсем понял!")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0, timeout=10)

'''
Создаем классы с ключем теста, или вызываем файлы по ключу который возьмем с кнопки.
'''
