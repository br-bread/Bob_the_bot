import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from data import db_session
from werkzeug.security import generate_password_hash, check_password_hash

from data.garden import PlantedPlant
from data.users import User
from data.plants import Plant
from db import DB

TOKEN = '5235508319:AAH_BNimCWuKBi1K2h71zey92tq1RMMmreg'
language = 'ru'
user = None
password = None
current_plant = None
talk = 0
add = 0
water = 0
waiting_for_name = 0
waiting_for_type = 0
chat_id = None

plants = {"Лисохвост": "Acalypha",
          "Звёздчатый кактус": "Astrophytum",
          "Азалия": "Azalea",
          "Бамбуковая пальма": "Chamaedorea",
          "Мандарин": "Citrus reticulata",
          "Фикус Эластика": "Ficus elastica",
          "Фреезия": "Freesia",
          "Вашингтония": "Washingtonia"}


def talking(update, context, story=False):
    reply_keyboard = [['Расскажи что-нибудь', 'Закончить разговор'],
                      []]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    if story:
        update.message.reply_text(
            "Могу рассказать вам одну историю.", reply_markup=markup)
    else:
        update.message.reply_text(
            "Я понимаю вас! Хорошая сегодня погода, кстати.", reply_markup=markup)


def watering(update, context):
    global water
    db_sess = db_session.create_session()
    data = db_sess.query(PlantedPlant).filter(PlantedPlant.id == current_plant).first()
    data.growth_param = data.growth_param + 5
    db_sess.commit()
    pl = db_sess.query(Plant).filter(Plant.id == current_plant).first()
    print(pl.latin_name, data.growth_param // 10 + 1)
    context.bot.send_photo(chat_id=update.message.chat_id,
                           photo=open(f'./data/graphics/{pl.latin_name}/img_{str(data.growth_param // 10 + 1)}.png', 'rb'))
    water = 0


def plant(update, context):
    global current_plant, waiting_for_name, waiting_for_type, add
    if not waiting_for_name:
        if update.message.text in plants.keys():
            current_plant = plants[update.message.text]
            update.message.reply_text(
                text=f"Отличный выбор! Как вы его назовёте?<i>(Введите имя растения)</i>",
                parse_mode=telegram.ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
            waiting_for_name = 1
            waiting_for_type = 0
        else:
            update.message.reply_text(
                text=f"У меня нет таких семян. Почему бы не выбрать из тех, "
                     f"что у меня есть? <i>(Выберите вариант из предлагаемых на клавиатуре)</i>",
                parse_mode=telegram.ParseMode.HTML)
    else:
        waiting_for_name = 0
        add = 0
        db_sess = db_session.create_session()
        data = db_sess.query(Plant).filter(Plant.latin_name == current_plant).first()
        plant_id = data.id

        data = db_sess.query(User).filter(User.login == user).first()
        data.current_plant_id = plant_id
        user_id = data.id

        DB.add("plant", update.message.text, user_id, plant_id)

        update.message.reply_text(
            text=f"Превосходно! {update.message.text} теперь в вашем саду!",
            parse_mode=telegram.ParseMode.HTML)

        context.bot.send_photo(chat_id=update.message.chat_id,
                               photo=open(f'./data/graphics/{current_plant}/img_1.png', 'rb'))
        current_plant = db_sess.query(PlantedPlant).filter(PlantedPlant.name == update.message.text).first()
        db_sess.commit()


def message(update, context):
    global user, password, talk, add, waiting_for_type, current_plant, water, chat_id
    chat_id = update.message.chat_id
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
                db_sess = db_session.create_session()
                current_plant = db_sess.query(User).filter(User.login == user).first().current_plant_id
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
    elif talk == 1:
        if update.message.text == "Закончить разговор":
            talk = 0
            update.message.reply_text(
                f"Буду рад снова пообщаться с вами, {user}.",
                reply_markup=ReplyKeyboardRemove())
        elif update.message.text == "Расскажи что-нибудь":
            talking(update, context, story=True)
        else:
            talking(update, context)
    elif add == 1:
        if not waiting_for_type and not waiting_for_name:
            button_list = [["Лисохвост", "Звёздчатый кактус", "Азалия", "Бамбуковая пальма"],
                           ["Мандарин", "Фикус Эластика", "Фреезия", "Вашингтония"]]
            reply_markup = ReplyKeyboardMarkup(button_list)
            update.message.reply_text(
                text=f"Не переживайте, {user}! Я буду вам помогать. Какое растение вы хотите посадить?",
                reply_markup=reply_markup)
            waiting_for_type = 1
        else:
            plant(update, context)
    elif water:
        watering(update, context)
    if password is not None and current_plant is None and not talk and not add and not water:
        button_list = [
            InlineKeyboardButton("Посадить растение", callback_data="add"),
            InlineKeyboardButton("Посмотреть сад", callback_data="look"),
            InlineKeyboardButton("Поговорить", callback_data="talk")
        ]
        reply_markup = InlineKeyboardMarkup([button_list])
        update.message.reply_text(
            f"Кажется, у вас нет текущего растения. Посадить новое?",
            parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
    if current_plant is not None and not talk and not add and not water:
        button_list = [
            InlineKeyboardButton("Полить растение", callback_data="water"),
            InlineKeyboardButton("Посмотреть сад", callback_data="look"),
            InlineKeyboardButton("Поговорить", callback_data="talk")
        ]
        reply_markup = InlineKeyboardMarkup([button_list])
        update.message.reply_text(
            f"Не хотите полить свое растение, {user}?",
            parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)


def button_pressed(update, context):
    global waiting_for_name, talk, add, water
    query = update.callback_query
    choice = query.data

    query.answer()
    if choice == "add":
        add = 1
        query.edit_message_text(
            text=f"Отлично! Вам придётся стараться и ухаживать за ним. Вы готовы?",
            parse_mode=telegram.ParseMode.HTML)
    elif choice == "talk":
        talk = 1
        query.edit_message_text(
            text=f"{user}, давайте поболтаем!",
            parse_mode=telegram.ParseMode.HTML)
    elif choice == "look":
        pass
    elif choice == "water":
        water = 1
        query.edit_message_text(
            text=f"Чтобы заботиться о ком-то, нужно научиться заботиться о себе."
                 f" Чтобы полить свое растение, вам нужно сделать что-то полезное для своего здоровья.",
            parse_mode=telegram.ParseMode.HTML)
        button_list = [["Выпил 2 стакана воды", "Спал 8 часов", "Прогулка 30мин - 1 час", "Прогулка > часа"],
                       ["Сделал зарядку", "Съел овощной салат", "Генеральная уборка", "Принял витамины"]]
        reply_markup = ReplyKeyboardMarkup(button_list)
        context.bot.send_message(chat_id=chat_id,
                                 text=f"Что такого вы недавно сделали?",
                                 reply_markup=reply_markup)

    elif choice == "Acalypha":
        query.edit_message_text(
            text=f"{user}, хороший выбор! Как вы назовёте своё растение?<i>(Введите имя для растения)</i>",
            parse_mode=telegram.ParseMode.HTML)
        waiting_for_name = 1


# Commands
def start(update, context):
    global user, password, current_plant, waiting_for_name
    user = None
    password = None
    current_plant = None
    waiting_for_name = 0
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
    if language == 'ru':
        update.message.reply_text("<i>Выход из аккаунта</i>", parse_mode=telegram.ParseMode.HTML)
    else:
        update.message.reply_text("<i>Logout</i>", parse_mode=telegram.ParseMode.HTML)

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
    updater.dispatcher.add_handler(CallbackQueryHandler(button_pressed))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
