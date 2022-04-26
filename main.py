import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from data import db_session
from db import DB

TOKEN = '5235508319:AAH_BNimCWuKBi1K2h71zey92tq1RMMmreg'
language = 'ru'
user = None


def start(update, context):
    global user
    user = None
    if language == 'ru':
        update.message.reply_text("Чтобы начать работу, нам нужно познакомиться! Как вас зовут? <i>(Введите логин)</i>",
                              parse_mode=telegram.ParseMode.HTML)
    else:
        update.message.reply_text("To start our work, we should get to know each other! What is your name? <i>(Enter your login)</i>",
                                  parse_mode=telegram.ParseMode.HTML)


# Commands
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
    global user
    user = None
    if language == 'ru':
        update.message.reply_text("<i>Выход из аккаунта</i>", parse_mode=telegram.ParseMode.HTML)
    else:
        update.message.reply_text("<i>Logout</i>", parse_mode=telegram.ParseMode.HTML)

    start(update)

def message(update, context):
    if user is None:
        # query
        pass



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
