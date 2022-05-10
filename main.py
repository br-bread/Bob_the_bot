import math

import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from data import db_session
from werkzeug.security import generate_password_hash

from data.garden import PlantedPlant
from data.users import User
from data.plants import Plant
from db import DB
import sqlalchemy
from random import choice
from PIL import Image

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

button_list_ru = [["Выпил 2 стакана воды", "Спал 8 часов", "Прогулка 30мин - 1 час", "Прогулка > часа"],
                  ["Сделал зарядку", "Съел овощной салат", "Генеральная уборка", "Принял витамины"]]

button_list_en = [["Drink 2 cups of water", "Sleep for 8 hours", "Walking 30m - 1h", "Walking > hour"],
                  ["Do exercises", "Eat vegetable salad", "Big cleanup", "Took vitamins"]]
plants = {"Лисохвост": "Acalypha",
          "Звёздчатый кактус": "Astrophytum",
          "Азалия": "Azalea",
          "Бамбуковая пальма": "Chamaedorea",
          "Мандарин": "Citrus reticulata",
          "Фикус Эластика": "Ficus elastica",
          "Фреезия": "Freesia",
          "Вашингтония": "Washingtonia",
          "Foxtail": "Acalypha",
          "Star cactus": "Astrophytum",
          "Azalea": "Azalea",
          "Bamboo palm": "Chamaedorea",
          "Tangerine": "Citrus reticulata",
          "Ficus elastica": "Ficus elastica",
          "Freesia": "Freesia",
          "Washingtonia": "Washingtonia"}


def talking(update, context, story=False):
    reply_keyboard = [['Расскажи что-нибудь', 'Закончить разговор'],
                      []]
    if language == "en":
        reply_keyboard = [['Tell me something', 'Finish conversation'],
                          []]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    if story:
        num = choice(["1", "2", "3"])
        file = open(f"./data/texts/stories/story{num}_{language}.txt", encoding="utf-8")
        data = file.read()
        update.message.reply_text(data)
        if num == "3":
            if language == "ru":
                update.message.reply_text(
                    f"Разве это плохо, {user}? Мне нравится мой цвет.", reply_markup=markup)
            else:
                update.message.reply_text(
                    f"Is that a bad thing, {user}? I really like green color.", reply_markup=markup)

    else:
        if language == "ru":
            update.message.reply_text(
                choice(["Я понимаю вас! Хорошая сегодня погода, кстати.", "Замечательно!",
                        "Кажется, мне стоит больше практиковаться в изучении языков...",
                        "Даже не знаю, что и сказать. Но вы можете попросить меня рассказать вам что-нибудь!"]),
                reply_markup=markup)
        else:
            update.message.reply_text(
                choice(["I understand! The weather is good today, by the way.", "Great!",
                        "I think i should practice more in languages",
                        "I really don't know what to say. But you can ask me to tell you something!"]),
                reply_markup=markup)


def watering(update, context):
    global water, current_plant, button_list_ru, button_list_en
    text = update.message.text
    if text not in button_list_ru[0] and text not in button_list_ru[1] and text not in button_list_en[0] and text not in \
            button_list_en[1]:
        if language == "ru":
            update.message.reply_text(
                text=f"Я не уверен, что это что-то полезное. Выберите что-то из того, что я предлагаю сделать! "
                     f"<i>(Выберите вариант из предлагаемых на клавиатуре)</i>",
                parse_mode=telegram.ParseMode.HTML)
        else:
            update.message.reply_text(
                text=f"I'm not sure if it is something useful. Choose something from what I suggest to do! "
                     f"<i>(Choose an option from the ones offered on the keyboard)</i>",
                parse_mode=telegram.ParseMode.HTML)
    else:
        db_sess = db_session.create_session()
        data = db_sess.query(PlantedPlant).filter(PlantedPlant.id == current_plant).first()
        plant_id = data.plant_id
        if text == button_list_ru[0][0] or text == button_list_ru[1][1] or text == button_list_ru[1][3] or text == \
                button_list_en[0][0] or text == button_list_en[1][1] or text == button_list_en[1][3]:
            data.growth_param = data.growth_param + 1
        elif text == button_list_ru[0][3] or text == button_list_ru[1][2] or text == button_list_en[0][3] or text == \
                button_list_en[1][2]:
            data.growth_param = data.growth_param + 5
        else:
            data.growth_param = data.growth_param + 3
        db_sess.commit()
        pl = db_sess.query(Plant).filter(Plant.id == plant_id).first()
        if language == "ru":
            update.message.reply_text(
                text=f"{data.name} растёт! Продолжайте поливать его.")
            context.bot.send_photo(chat_id=update.message.chat_id,
                                   photo=open(
                                       f'./data/graphics/{pl.latin_name}/img_{str(data.growth_param // 10 + 1)}.png',
                                       'rb'), reply_markup=ReplyKeyboardRemove())
        else:
            update.message.reply_text(
                text=f"{data.name} is growing! Keep pouring it.")
            context.bot.send_photo(chat_id=update.message.chat_id,
                                   photo=open(
                                       f'./data/graphics/{pl.latin_name}/img_{str(data.growth_param // 10 + 1)}.png',
                                       'rb'), reply_markup=ReplyKeyboardRemove())
        if data.growth_param // 10 + 1 == 4:
            current_plant = None
            uuser = db_sess.query(User).filter(User.login == user).first()
            uuser.current_plant_id = sqlalchemy.sql.null()
            if language == "ru":
                update.message.reply_text(
                    text=f"Посмотрите, как вырос {data.name}! Теперь вы можете посадить другое растение.",
                    parse_mode=telegram.ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
            else:
                update.message.reply_text(
                    text=f"Look how {data.name} grown up! Now you can plant another plant.",
                    parse_mode=telegram.ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
            db_sess.commit()

        water = 0


def plant(update, context):
    global current_plant, waiting_for_name, waiting_for_type, add
    if not waiting_for_name:
        if update.message.text in plants.keys():
            current_plant = plants[update.message.text]
            file = open(f"./data/texts/{current_plant}_info_{language}.txt", encoding="utf-8")
            data = file.read()
            update.message.reply_text(data)
            if language == "ru":
                update.message.reply_text(
                    text=f"Отличный выбор! Как вы его назовёте?<i>(Введите имя растения)</i>",
                    parse_mode=telegram.ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
            else:
                update.message.reply_text(
                    text=f"Nice choice! What name will you give it?<i>(Enter the name of your plant)</i>",
                    parse_mode=telegram.ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
            waiting_for_name = 1
            waiting_for_type = 0
        else:
            update.message.reply_text(
                text=f"I don't have any such seeds. Why don't you choose from those "
                     f"I have? <i>(Choose an option from the ones offered on the keyboard)</i>",
                parse_mode=telegram.ParseMode.HTML)
    else:
        db_sess = db_session.create_session()
        uuser = db_sess.query(User).filter(User.login == user).first()
        is_planted = db_sess.query(PlantedPlant).filter(PlantedPlant.name == update.message.text,
                                                        PlantedPlant.user_id == uuser.id).first()
        if is_planted:
            if language == "ru":
                update.message.reply_text(
                    text=f"Кажется, в вашем саду уже есть растение с таким именем.<i>(Введите другое имя)</i>",
                    parse_mode=telegram.ParseMode.HTML)
            else:
                update.message.reply_text(
                    text=f"Seems that there is already a plant with this name in your garden.<i>(Choose another name)</i>",
                    parse_mode=telegram.ParseMode.HTML)
        else:
            waiting_for_name = 0
            add = 0
            plant_id = db_sess.query(Plant).filter(Plant.latin_name == current_plant).first().id

            DB.add("plant", update.message.text, uuser.id, plant_id)
            current_plant = uuser.current_plant_id = db_sess.query(PlantedPlant).filter(
                PlantedPlant.user_id == uuser.id,
                PlantedPlant.name == update.message.text).first().id
            if language == "ru":
                update.message.reply_text(
                    text=f"Превосходно! {update.message.text} теперь в вашем саду!",
                    parse_mode=telegram.ParseMode.HTML)
            else:
                update.message.reply_text(
                    text=f"Cool! Now {update.message.text} is in your garden!",
                    parse_mode=telegram.ParseMode.HTML)
            context.bot.send_photo(chat_id=update.message.chat_id,
                                   photo=open(
                                       f'./data/graphics/{db_sess.query(Plant).filter(Plant.id == plant_id).first().latin_name}/img_1.png',
                                       'rb'))

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
        if update.message.text == "Закончить разговор" or update.message.text == "Finish conversation":
            talk = 0
            if language == "ru":
                update.message.reply_text(
                    f"Буду рад снова пообщаться с вами, {user}.",
                    reply_markup=ReplyKeyboardRemove())
            else:
                update.message.reply_text(
                    f"I will glad to talk to you again, {user}.",
                    reply_markup=ReplyKeyboardRemove())
        elif update.message.text == "Расскажи что-нибудь" or update.message.text == "Tell me something":
            talking(update, context, story=True)
        else:
            talking(update, context)
    elif add == 1:
        if not waiting_for_type and not waiting_for_name:
            button_list_ru = [["Лисохвост", "Звёздчатый кактус", "Азалия", "Бамбуковая пальма"],
                              ["Мандарин", "Фикус Эластика", "Фреезия", "Вашингтония"]]
            button_list_en = [["Foxtail", "Star cactus", "Azalea", "Bamboo palm"],
                              ["Tangerine", "Ficus elastica", "Freesia", "Washingtonia"]]
            if language == "ru":
                reply_markup = ReplyKeyboardMarkup(button_list_ru)
                update.message.reply_text(
                    text=f"Не переживайте, {user}! Я буду вам помогать. Какое растение вы хотите посадить?",
                    reply_markup=reply_markup)
            else:
                reply_markup = ReplyKeyboardMarkup(button_list_en)
                update.message.reply_text(
                    text=f"Don't worry, {user}! I will help you. What plant do you want to plant?",
                    reply_markup=reply_markup)
            waiting_for_type = 1
        else:
            plant(update, context)
    elif water:
        watering(update, context)
    if password is not None and current_plant is None and not talk and not add and not water:
        button_list_ru = [
            InlineKeyboardButton("Посадить растение", callback_data="add"),
            InlineKeyboardButton("Посмотреть сад", callback_data="look"),
            InlineKeyboardButton("Поговорить", callback_data="talk")
        ]
        button_list_en = [
            InlineKeyboardButton("Plant a plant", callback_data="add"),
            InlineKeyboardButton("View the garden", callback_data="look"),
            InlineKeyboardButton("Talk", callback_data="talk")
        ]
        if language == "ru":
            reply_markup = InlineKeyboardMarkup([button_list_ru])
            update.message.reply_text(
                f"Кажется, у вас нет текущего растения. Посадить новое?",
                parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
        else:
            reply_markup = InlineKeyboardMarkup([button_list_en])
            update.message.reply_text(
                f"Seems you don't have a current plant. Do you want to plant a new one?",
                parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
    if current_plant is not None and not talk and not add and not water:
        button_list_ru = [
            InlineKeyboardButton("Полить растение", callback_data="water"),
            InlineKeyboardButton("Посмотреть сад", callback_data="look"),
            InlineKeyboardButton("Поговорить", callback_data="talk")
        ]
        button_list_en = [
            InlineKeyboardButton("Pour a plant", callback_data="water"),
            InlineKeyboardButton("View the garden", callback_data="look"),
            InlineKeyboardButton("Talk", callback_data="talk")
        ]
        if language == "ru":
            reply_markup = InlineKeyboardMarkup([button_list_ru])
            update.message.reply_text(
                f"Не хотите полить свое растение, {user}?",
                parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
        else:
            reply_markup = InlineKeyboardMarkup([button_list_en])
            update.message.reply_text(
                f"Do you want to pour your plant, {user}?",
                parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)


def button_pressed(update, context):
    global waiting_for_name, talk, add, water, button_list_en, button_list_ru
    query = update.callback_query
    choice = query.data

    query.answer()
    if choice == "add":
        add = 1
        if language == "ru":
            query.edit_message_text(
            text=f"Отлично! Вам придётся стараться и ухаживать за ним. Вы готовы?",
            parse_mode=telegram.ParseMode.HTML)
        else:
            query.edit_message_text(
                text=f"Great! You will have to do your best and take care of it. Are you ready?",
                parse_mode=telegram.ParseMode.HTML)
    elif choice == "talk":
        talk = 1
        if language == "ru":
            query.edit_message_text(
                text=f"{user}, давайте поболтаем!",
                parse_mode=telegram.ParseMode.HTML)
        else:
            query.edit_message_text(
                text=f"Let's talk, {user}!",
                parse_mode=telegram.ParseMode.HTML)
    elif choice == "look":
        db_sess = db_session.create_session()
        uuser = db_sess.query(User).filter(User.login == user).first()
        user_plants = db_sess.query(PlantedPlant).filter(PlantedPlant.user_id == uuser.id).all()
        if not user_plants:
            if language == "ru":
                query.edit_message_text(
                    text=f"Похоже ваш сад ещё пустой. Но вы можете это исправить!",
                    parse_mode=telegram.ParseMode.HTML)
            else:
                query.edit_message_text(
                    text=f"Looks like your garden is empty. But you can change it!",
                    parse_mode=telegram.ParseMode.HTML)
        else:
            if language == "ru":
                query.edit_message_text(
                    text=f"Хотите посмотреть свой сад? Хорошо. Взгляните, я навёл небольшой порядок.",
                    parse_mode=telegram.ParseMode.HTML)
            else:
                query.edit_message_text(
                    text=f"Do you want to see your garden? Good. Look, I've organized it a little.",
                    parse_mode=telegram.ParseMode.HTML)
            create_garden()
            context.bot.send_photo(chat_id=chat_id, photo=open(f'./data/graphics/garden.png', 'rb'))
    elif choice == "water":
        water = 1
        if language == "ru":
            query.edit_message_text(
                text=f"Чтобы заботиться о ком-то, нужно научиться заботиться о себе."
                     f" Чтобы полить свое растение, вам нужно сделать что-то полезное для своего здоровья.",
                parse_mode=telegram.ParseMode.HTML)
            reply_markup = ReplyKeyboardMarkup(button_list_ru)
            context.bot.send_message(chat_id=chat_id,
                                     text=f"Что такого вы недавно сделали?",
                                     reply_markup=reply_markup)
        else:
            query.edit_message_text(
                text=f"To take care of someone, you should learn to take care of yourself."
                     f" To water your plant, you need to do something useful for your health.",
                parse_mode=telegram.ParseMode.HTML)
            reply_markup = ReplyKeyboardMarkup(button_list_en)
            context.bot.send_message(chat_id=chat_id,
                                     text=f"What useful things have you done?",
                                     reply_markup=reply_markup)


def create_garden():
    db_sess = db_session.create_session()
    uuser = db_sess.query(User).filter(User.login == user).first()
    user_plants = db_sess.query(PlantedPlant).filter(PlantedPlant.user_id == uuser.id).all()
    size = int(math.sqrt(len(user_plants))) + 1 * bool(math.sqrt(len(user_plants)) % 1 != 0)
    if size < 3:
        k = 512
    else:
        k = 256

    garden_image = Image.new("RGB", (k * size, k * size), (255, 255, 255))
    print(user_plants)
    for i in range(1, len(user_plants) + 1):
        img = Image.open(
            f'./data/graphics/{db_sess.query(Plant).filter(Plant.id == user_plants[i - 1].plant_id).first().latin_name}'
            f'/img_{str(user_plants[i - 1].growth_param // 10 + 1)}.png').resize((k, k))
        garden_image.paste(img, ((size - i % size - 1) * k, (i // size + 1 * bool(i % size) - 1) * k))
        print((size - i % size) * k, (i // size + 1 * bool(i % size)) * k)
        garden_image.save(f"./data/graphics/garden{str(i)}.png")

    garden_image.save("./data/graphics/garden.png")


# Commands
def start(update, context):
    global user, password, current_plant, waiting_for_name, talk, add, water, waiting_for_type, chat_id
    user = None
    password = None
    current_plant = None
    waiting_for_name = 0
    talk = 0
    add = 0
    water = 0
    waiting_for_type = 0
    chat_id = None
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
        update.message.reply_text("<i>Выход из аккаунта</i>", parse_mode=telegram.ParseMode.HTML,
                                  reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text("<i>Logout</i>", parse_mode=telegram.ParseMode.HTML,
                                  reply_markup=ReplyKeyboardRemove())

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
