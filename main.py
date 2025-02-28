# def my_decorator(func):
#     def wrapper(a, b):
#         print("hello")
#         func(a, b)
#         print("how are you")
#     return wrapper
#
# @my_decorator
# def say_name(a, b):
#     print(a, b)
#
#
# say_name("A", "B")

import random
import telebot
from telebot import types
import config
import wikipedia
import re
import sqlite3

# создаём .бд атрибут check_same_thread - позволяет использование соединения в разных потоках
conn = sqlite3.connect("users.db", check_same_thread=False)
# объект-курсор для обращения в бд (поиск, добавить, удалить и тд..)
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users(id INT);") # создание запроса на создание таблицы
conn.commit() # сохранение данных

bot = telebot.TeleBot(config.token)

game = False
nun = False
is_wiki = False
admins = [6729175936]
text = ""
link = ""
clients = []
statia = ["Москва", "Питер", "Шаурма"]



# @bot.message_handler(commands=["random_statia"])
# def rand_statia(message):
#     choice_statia = random.choice(statia)
#     bot.send_message(message.chat.id, comm_wikipedia(choice_statia))

@bot.message_handler(commands=["start"])
def test(message):
    if message.chat.id in admins:
        help(message)
    else:
        info = cur.execute("SELECT * FROM users WHERE id=?", (message.chat.id,)).fetchone()
        if not info:
            cur.execute("INSERT INTO users (id) VALUES (?)", (message.chat.id,))
            conn.commit()
            bot.send_message(message.chat.id, "Теперь вы будете получать рассылку!")

    # print(message)
    # markup_inline = types.InlineKeyboardMarkup()
    # btn_y = types.InlineKeyboardButton(text="yes", callback_data="yes")
    # btn_n = types.InlineKeyboardButton(text="no", callback_data="no")
    # markup_inline.add(btn_y, btn_n)
    # bot.send_message(message.chat.id, "Хочешь продолжить?", reply_markup=markup_inline)


def help(message):
    admin_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создали клаву
    admin_markup.add(types.KeyboardButton("Создать текст для рассылки"))  # создали кнопку
    admin_markup.add(types.KeyboardButton("Создать ссылку для рассылки"))  # создали кнопку
    admin_markup.add(types.KeyboardButton("Показать сообщение для рассылки"))  # создали кнопку
    admin_markup.add(types.KeyboardButton("Начать рассылку"))  # создали кнопку
    admin_markup.add(types.KeyboardButton("Помощь"))  # создали кнопку
    bot.send_message(message.chat.id, "Команды бота: \n"
                                      "/create_text - создать текст для рассылки. \n"
                                      "/create_link - создать ссылку для рассылки \n"
                                      "/show_message - показать сообщение для рассылки \n"
                                      "/start_linking - начать рассылку \n"
                                      "/help - помощь", reply_markup=admin_markup)

@bot.message_handler(commands=["show_message"])
def message_show(message):
    global text
    global link
    if message.chat.id in admins:
        bot.send_message(message.chat.id, f"Сохранённый текст: {text}. Сохранённая ссылка: {link}")






@bot.message_handler(commands=["create_link"])
def edit_link(message):
    if message.chat.id in admins:
        m = bot.send_message(message.chat.id, "Введи ссылку для рассылки")
        bot.register_next_step_handler(m, add_link)


def add_link(message):
    global link
    regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # проверка dot
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # проверка ip 
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if message.text is not None and regex.search(message.text):
        link = message.text
        bot.send_message(message.chat.id, f"Сохранил ссылку:{link}")
    else:
        m = bot.send_message(message.chat.id, "Ссылка некорректная")
        bot.register_next_step_handler(m, add_link)


@bot.message_handler(commands=["start_linking"])
def edit_start_linking(message):
    global text, link
    if message.chat.id in admins:
        if text != "":
            if link != "":
                cur.execute("SELECT id FROM users")
                massive = cur.fetchall()
                print(massive)
                for client_id in massive:
                    id = client_id[0]
                    sending(id)
                else:
                    text = ""
                    link = ""
            else:
                bot.send_message(message.chat.id, "Ссылка отсутсвует, заполни перед отправкой")
        else:
            bot.send_message(message.chat.id, "Текст отсутсвует, заполни перед отправкой")


def sending(id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Ссылка на сайт", url=link))
    bot.send_message(id, text, reply_markup=markup)


@bot.message_handler(commands=["create_text"])
def edit_message(message):
    if message.chat.id in admins:
        m = bot.send_message(message.chat.id, "Введи текст для рассылки")
        bot.register_next_step_handler(m, add_text)


def add_text(message):
    global text
    text = message.text
    if text not in ["Скиньтесь админу на покупку факторио"]:
        bot.send_message(message.chat.id, f"Сохранённый текст: {text}")
    else:
        bot.send_message(message.chat.id, "Ошибка")


@bot.message_handler(commands=["wikipedia"])
def comm_wikipedia(message):
    markup_wikipedia = types.InlineKeyboardMarkup()
    btn_search = types.InlineKeyboardButton(text="yes want", callback_data="yes want")
    btn_no_search = types.InlineKeyboardButton(text="no want", callback_data="no want")
    markup_wikipedia.add(btn_search, btn_no_search)
    bot.send_message(message.chat.id, "Хочешь найти что-нибудь?", reply_markup=markup_wikipedia)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global is_wiki
    try:
        if call.message:
            if call.data == "yes want":
                bot.send_message(call.message.chat.id, "wiki active")
                is_wiki = True
            if call.data == "yes":
                bot.send_message(call.message.chat.id, "что ты нажал кнопку да")
                reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создаёт клавиатуру reply_markup
                btn_id = types.KeyboardButton("id")  # делает кнопку btn_id
                btn_usr = types.KeyboardButton("usr")  # делает кнопку btn_usr
                reply_markup.add(btn_id, btn_usr)  # добавляет кнопки btn_id, btn_usr в клавиатуру reply_markup
                bot.send_message(call.message.chat.id, "что тебе показать?", reply_markup=reply_markup)

            if call.data == "yes want":
                is_wiki = True
                print("rrrff")
                bot.send_message(call.message.id, "rrrff wiki active")

            if call.data == "no":
                bot.send_message(call.message.chat.id, "нажал кнопку нет")
    except Exception as e:
        print(repr(e))


@bot.message_handler(commands=["hello"])
def test(message):
    bot.send_message(message.chat.id, "отправил сообщение")


@bot.message_handler(content_types=["text"])
def get_text(message):
    if is_wiki is True:
        user_text = comm_wikipedia(message.text)
        bot.send_message(message.chat.id, user_text)
    if "привет" == message.text:
        bot.send_message(message.chat.id, "ты написал привет")
    elif "id" == message.text:
        bot.send_message(message.chat.id, f"вот ваш id: {message.from_user.id}")
    elif "usr" == message.text:
        bot.send_message(message.chat.id, f"вот ваш username: {message.from_user.username}")
    elif "Создать текст для рассылки" == message.text:
        bot.send_message(message.chat.id, f"вот текст для рассылки: {add_text}")
        edit_message(message)
    elif "Создать ссылку для рассылки" == message.text:
        bot.send_message(message.chat.id, f"вот ссылка для рассылки: {add_link}")
        edit_link(message)
    elif "Начать рассылку" == message.text:
        bot.send_message(message.chat.id, f"вот сообщение рассылки: {add_text, add_link}")
        edit_start_linking(message)
    elif "Показать сообщение для рассылки" == message.text:
        message_show(message)



bot.infinity_polling()
