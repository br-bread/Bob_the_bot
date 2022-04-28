import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from data import db_session
from werkzeug.security import generate_password_hash, check_password_hash

from data.users import User
from db import DB

TOKEN = '5235508319:AAH_BNimCWuKBi1K2h71zey92tq1RMMmreg'
language = 'ru'
user = None
password = None


# Commands
def start(update, context):
    global user, password
    user = None
    password = None
    if language == 'ru':
        update.message.reply_text("Чтобы начать работу, нам нужно познакомиться! Как вас зовут? <i>(Введите логин)</i>",
                                  parse_mode=telegram.ParseMode.HTML)
    else:
        update.message.reply_text(
            "To start our work, we should get to know each other! What is your name? <i>(Enter your login)</i>",
            parse_mode=telegram.ParseMode.HTML)


def help(update, context):
    file = open(f"./data/texts/help_{language}.txt", encoding="utf-8")
    data = file.read()
    update.message.reply_text(data, parse_mode=telegram.ParseMode.HTML)


def info(update, context):
    file = open(f"./data/texts/description_{language}.txt", encoding="utf-8")
    data = file.read()
    update.message.reply_text(data)


def language_en(update, context):
    global language
    language = 'en'
    update.message.reply_text("The language has changed to English.")


def language_ru(update, context):
    global language
    language = 'ru'
    update.message.reply_text("Язык изменён на русский.")


def logout(update, context):
    global user, password
    user = None
    password = None
    if language == 'ru':
        update.message.reply_text("<i>Выход из аккаунта</i>", parse_mode=telegram.ParseMode.HTML)
    else:
        update.message.reply_text("<i>Logout</i>", parse_mode=telegram.ParseMode.HTML)

    start(update, context)


def message(update, context):
    global user, password
    if user is None:
        user = update.message.text
        user_in_base = 0
        db_sess = db_session.create_session()
        data = db_sess.query(User).filter(User.login == user).first()
        if data is not None:
            user_in_base = 1

        if not user_in_base:
            if language == 'ru':
                update.message.reply_text(
                    "Кажется, я вас не знаю... Давайте создадим профиль! <i>(Введите пароль)</i>",
                    parse_mode=telegram.ParseMode.HTML)
            else:
                update.message.reply_text(
                    "Seems like i don't know who you are... Let's create a profile! <i>(Enter password)</i>",
                    parse_mode=telegram.ParseMode.HTML)
        else:
            if language == 'ru':
                update.message.reply_text(
                    f"Привет, {user}! Мне нужно убедится, что это вы. <i>(Введите пароль)</i>",
                    parse_mode=telegram.ParseMode.HTML)
            else:
                update.message.reply_text(
                    f"Hi, {user}! I need to make sure it's you. <i>(Enter password)</i>",
                    parse_mode=telegram.ParseMode.HTML)

    elif password is None:
        user_in_base = 0
        db_sess = db_session.create_session()
        data = db_sess.query(User).filter(User.login == user).first()
        if data is not None:
            user_in_base = 1

        password = update.message.text

        if not user_in_base:
            DB.add("user", user, generate_password_hash(password))
            if language == 'ru':
                update.message.reply_text(
                    f"<i>Регистрация прошла успешно</i>",
                    parse_mode=telegram.ParseMode.HTML)
            else:
                update.message.reply_text(
                    f"<i>Registration was succeed</i>",
                    parse_mode=telegram.ParseMode.HTML)
        else:
            password_is_correct = data.check_password(password)
            if password_is_correct:
                if language == 'ru':
                    update.message.reply_text(
                        f"<i>Авторизация прошла успешно</i>",
                        parse_mode=telegram.ParseMode.HTML)
                else:
                    update.message.reply_text(
                        f"<i>Authorisation was succeed</i>",
                        parse_mode=telegram.ParseMode.HTML)
            else:
                if language == 'ru':
                    update.message.reply_text(
                        f"<i>Неверный пароль или логин уже занят</i>",
                        parse_mode=telegram.ParseMode.HTML)
                else:
                    update.message.reply_text(
                        f"<i>Invalid password or login is already occupied</i>",
                        parse_mode=telegram.ParseMode.HTML)
                start(update, context)




def main():
    db_session.global_init("database/db.db")
    # DB.add("user", "Bobochek", "sdflkskdg")
    # DB.add("plant", "hop", 4, 3)
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    text_handler = MessageHandler(Filters.text & ~Filters.command, message)

    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("logout", logout))
    dp.add_handler(CommandHandler("language_en", language_en))
    dp.add_handler(CommandHandler("language_ru", language_ru))
    dp.add_handler(text_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
