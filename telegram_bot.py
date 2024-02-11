from decouple import config
from telegram_parser import login, profiles, my_profile
from decouple import config
import telebot
import requests
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import webbrowser

bot_token = '6801749167:AAFdFCRfctxH5s56oytwvOM9lObILv7hrzc'
# Создаем экземпляр бота
bot = telebot.TeleBot(bot_token)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton('login', callback_data='login'))
    bot.send_message(message.chat.id, "Привет! Это публичный бот, публичного сайта trello_hackaton. Чтобы воити нажимай /login", reply_markup=keyboard)

# Обработчик команды /login
@bot.message_handler(commands=['login'])
def login_message(message):
    bot.send_message(message.chat.id, "Введите свой email:")
    bot.register_next_step_handler(message, process_email_step)

# Обработчик следующего шага после ввода email
def process_email_step(message):
    email = message.text
    bot.send_message(message.chat.id, "Введите пароль:")
    bot.register_next_step_handler(message, process_password_step, email)

# Обработчик следующего шага после ввода пароля
access_token = ''
def process_password_step(message, email):
    password = message.text
    global access_token

    response = login(email, password)
    if response:
        access_token = response.get('access')
        bot.send_message(message.chat.id, "Успешный вход!")
    else:
        bot.send_message(message.chat.id, "Ой кажется у вас не правильные данные попробуйте снова!\n Пожалуйста проверьте активировали ли вы свой аккаунт.")

@bot.message_handler(commands=['profiles'])
def trello_profiles(message):
    response = profiles()
    if message == 'profiles':
        if response:
            bot.send_message(message.chat.id, str(response))
        else:
            bot.send_message(message.chat.id, 'У тебя в коде ошибка')

@bot.message_handler(commands=['my_profile'])
def trello_my_profile(message):
    
    response = my_profile(access_token)
    if response:
        bot.send_message(message.chat.id, str(response))
    else:
        bot.send_message(message.chat.id, 'Вы не зарегистрированы')


# Запускаем бота
bot.polling()