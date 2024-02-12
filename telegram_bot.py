from telegram_parser import login, profiles, my_profile, feeds, posts, my_favorites, recomendation, exit, user_acces_token_and_id
import telebot
import requests

bot_token = '6801749167:AAFdFCRfctxH5s56oytwvOM9lObILv7hrzc'
# Создаем экземпляр бота
bot = telebot.TeleBot(bot_token)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Это публичный бот, публичного сайта trello_hackaton. Чтобы воити нажимай /login")

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

def process_password_step(message, email):
    global user_acces_token_and_id
    password = message.text

    response = login(email, password)
    if response:
        token = {message.chat.id: response.get('access')}
        user_acces_token_and_id.update(token)
        bot.send_message(message.chat.id, "Поздравляем вы успешно вошли в свой аккаунт!\n Теперь вы можете выполнять разные функции в twitter_hackaton.") # reply_markup=keyboard
    else:
        bot.send_message(message.chat.id, "Ой кажется у вас не правильные данные попробуйте снова!\n Чтобы перезапустить бота нажмите на /start")


@bot.message_handler(commands=['profiles'])
def profiles_message(message):
    response = profiles()
    if response:
        bot.send_message(message.chat.id, str(response))
    else:
        bot.send_message(message.chat.id, 'У тебя в коде ошибка')

@bot.message_handler(commands=['my_profile'])
def my_profile_message(message):
    global user_acces_token_and_id
    response = my_profile(user_acces_token_and_id.get(message.chat.id))
    if response == 401:
        bot.send_message(message.chat.id, 'Кажется время вашего токена истекло,\nпожалуйста перезайдите свой аккаунт /login')
    elif response:
        bot.send_message(message.chat.id, str(response))

    else:
        bot.send_message(message.chat.id, 'Нет профилья')

@bot.message_handler(commands=['feeds'])
def feeds_message(message):
    global user_acces_token_and_id
    response = feeds(user_acces_token_and_id.get(message.chat.id))
    if response == 401:
        bot.send_message(message.chat.id, 'Кажется время вашего токена истекло,\nпожалуйста перезайдите свой аккаунт /login')
    elif response:
        for post in response:
            image = post.get('image')
            if image:
                http_photo = requests.get(image)
                if http_photo.status_code == 200:
                    bot.send_photo(message.chat.id, http_photo.content, caption=str(post.get('post')))
            else:
                bot.send_message(message.chat.id, str(post.get('post')))
    else:
        bot.send_message(message.chat.id, 'Нету постов пользователей на которых вы подписаны.')


@bot.message_handler(commands=['posts'])
def posts_message(message):
    response = posts()
    if response:
        for post in response:
            image = post.get('image')
            if image:
                http_photo = requests.get(image)
                if http_photo.status_code == 200:
                    bot.send_photo(message.chat.id, http_photo.content, caption=str(post.get('content')))
            else:
                bot.send_message(message.chat.id, str(post.get('content')))
    else:
        bot.send_message(message.chat.id, 'В twitter_hackaton нет постов')


@bot.message_handler(commands=['my_favorites'])
def my_favorites_message(message):
    global user_acces_token_and_id
    response = my_favorites(user_acces_token_and_id.get(message.chat.id))
    if response == 401:
        bot.send_message(message.chat.id, 'Кажется время вашего токена истекло,\nпожалуйста перезайдите свой аккаунт /login')
    elif response:
        for post in response:
            image = post.get('image')
            if image:
                http_photo = requests.get(image)
                if http_photo.status_code == 200:
                    bot.send_photo(message.chat.id, http_photo.content, caption=str(post.get('post')))
            else:
                bot.send_message(message.chat.id, str(post.get('post')))
    elif response == 401:
        bot.send_message(message.chat.id, 'Кажется время вашего токена истекло,\nпожалуйста перезайдите свой аккаунт /login')
    else:
        bot.send_message(message.chat.id, 'Нету избранных постов')


@bot.message_handler(commands=['recomendation'])
def recomendation_message(message):
    global user_acces_token_and_id
    response = recomendation(user_acces_token_and_id.get(message.chat.id))
    if response == 401:
        bot.send_message(message.chat.id, 'Кажется время вашего токена истекло,\nпожалуйста перезайдите свой аккаунт /login')
    elif response:
        for post in response:
            image = 'http://localhost' + post.get('image')
            if image:
                http_photo = requests.get(image)
                if http_photo.status_code == 200:
                    bot.send_photo(message.chat.id, http_photo.content, caption=str(post.get('content')))
            else:
                bot.send_message(message.chat.id, str(post.get('content')))
    else:
        bot.send_message(message.chat.id, 'Нету для вас постов которых хотели бы по рекомендовать')

@bot.message_handler(commands=['exit'])
def recomendation_message(message):
    response = exit(message.chat.id)
    bot.send_message(message.chat.id, response)

# Запускаем бота
bot.polling()