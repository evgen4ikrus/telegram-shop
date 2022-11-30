import logging
import os

import redis
import telegram
from environs import Env
from requests.exceptions import HTTPError
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

from format_message import create_cart_description, create_product_description
from log_helpers import TelegramLogsHandler
from moltin_helpers import (add_product_to_cart, create_customer,
                            delete_product_from_cart, get_all_products,
                            get_cart_items, get_file_by_id,
                            get_moltin_access_token, get_product_by_id,
                            get_product_files)

_database = None
logger = logging.getLogger('tg_bot')

MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT = None, None


def get_menu_keyboard():
    global MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT
    MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT = get_moltin_access_token(moltin_client_id, motlin_client_secret,
                                                                    MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT)
    products = get_all_products(MOTLIN_ACCESS_TOKEN)
    keyboard = [
        [InlineKeyboardButton(product.get('attributes').get('name'), callback_data=product.get('id'))]
        for product in products
    ]
    keyboard.append([InlineKeyboardButton('Корзина', callback_data='Корзина')])
    return keyboard


def get_cart_keyboard(cart_items):
    keyboard = [
        [InlineKeyboardButton(f"Убрать из корзины {item.get('name')}", callback_data=item.get('id'))]
        for item in cart_items
    ]
    keyboard.insert(0, [InlineKeyboardButton('Оплатить', callback_data='Оплатить')])
    keyboard.append([InlineKeyboardButton('В меню', callback_data='Меню')])
    return keyboard


def start(bot, update):
    keyboard = get_menu_keyboard()
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='Главное меню:', reply_markup=reply_markup)
    return 'HANDLE_MENU'


def handle_menu(bot, update):
    global MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT
    MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT = get_moltin_access_token(moltin_client_id, motlin_client_secret,
                                                                    MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT)
    query = update.callback_query
    if query.data == 'Корзина':
        cart_items = get_cart_items(MOTLIN_ACCESS_TOKEN, query.message.chat_id)
        message = create_cart_description(cart_items)
        keyboard = get_cart_keyboard(cart_items)
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(text=message, chat_id=query.message.chat_id, reply_markup=reply_markup)
        return 'HANDLE_CART'
    product_id = '{}'.format(query.data)
    product = get_product_by_id(MOTLIN_ACCESS_TOKEN, product_id)
    message = create_product_description(product)
    product_files = get_product_files(MOTLIN_ACCESS_TOKEN, product_id)
    keyboard = [
        [InlineKeyboardButton('1 кг', callback_data=f'1 {product_id}'),
         InlineKeyboardButton('3 кг', callback_data=f'3 {product_id}'),
         InlineKeyboardButton('5 кг', callback_data=f'5 {product_id}')],
        [InlineKeyboardButton('Корзина', callback_data='Корзина')],
        [InlineKeyboardButton('Назад', callback_data='Назад')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if product_files:
        file_id = product_files[0].get('id')
        file = get_file_by_id(MOTLIN_ACCESS_TOKEN, file_id)
        file_link = file.get('link').get('href')
        bot.send_photo(chat_id=query.message.chat_id, caption=message, photo=file_link, reply_markup=reply_markup)
        bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        return 'HANDLE_DESCRIPTION'
    bot.send_message(text=message, chat_id=query.message.chat_id, reply_markup=reply_markup)
    return 'HANDLE_DESCRIPTION'


def handle_description(bot, update):
    global MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT
    MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT = get_moltin_access_token(moltin_client_id, motlin_client_secret,
                                                                    MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT)
    query = update.callback_query
    if query.data == 'Назад':
        keyboard = get_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Главное меню:'
        bot.send_message(text=message, chat_id=query.message.chat_id, reply_markup=reply_markup)
        bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        return 'HANDLE_MENU'
    if query.data == 'Корзина':
        cart_items = get_cart_items(MOTLIN_ACCESS_TOKEN, query.message.chat_id)
        message = create_cart_description(cart_items)
        keyboard = get_cart_keyboard(cart_items)
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(text=message, chat_id=query.message.chat_id, reply_markup=reply_markup)
        return 'HANDLE_CART'
    command, product_id = query.data.split()
    add_product_to_cart(MOTLIN_ACCESS_TOKEN, product_id, query.message.chat_id, command)
    update.callback_query.answer("Товар добавлен в корзину")
    return 'HANDLE_DESCRIPTION'


def handle_cart(bot, update):
    global MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT
    MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT = get_moltin_access_token(moltin_client_id, motlin_client_secret,
                                                                    MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT)
    query = update.callback_query
    if query.data == 'Меню':
        keyboard = get_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Главное меню:'
        bot.send_message(text=message, chat_id=query.message.chat_id, reply_markup=reply_markup)
        return 'HANDLE_MENU'
    if query.data == 'Оплатить':
        message = 'Пожалуйста введите Вашу электронную почту:'
        bot.send_message(text=message, chat_id=query.message.chat_id)
        return 'HANDLE_WAITING_EMAIL'
    delete_product_from_cart(MOTLIN_ACCESS_TOKEN, query.message.chat_id, query.data)
    cart_items = get_cart_items(MOTLIN_ACCESS_TOKEN, query.message.chat_id)
    message = create_cart_description(cart_items)
    keyboard = get_cart_keyboard(cart_items)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.answer("Товар удален из корзину")
    bot.send_message(text=message, chat_id=query.message.chat_id, reply_markup=reply_markup)
    return 'HANDLE_CART'


def handle_watting_email(bot, update):
    global MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT
    user = update.effective_user
    name = f"{user.first_name} id:{user.id}"
    email = update.message.text
    MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT = get_moltin_access_token(moltin_client_id, motlin_client_secret,
                                                                    MOTLIN_ACCESS_TOKEN, TOKEN_CREATED_AT)
    try:
        create_customer(MOTLIN_ACCESS_TOKEN, name, email)
    except HTTPError:
        message = 'Произошла ошибка, возможно вы прислали несуществующий email. Попробуйте повторить попытку:'
        bot.send_message(text=message, chat_id=update.message.chat_id)
        return 'HANDLE_WAITING_EMAIL'
    message = f'Вы прислали мне эту эл. почту: {email}'
    bot.send_message(text=message, chat_id=update.message.chat_id)
    return 'HANDLE_WAITING_EMAIL'


def handle_users_reply(bot, update):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode('utf-8')

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'HANDLE_WAITING_EMAIL': handle_watting_email,
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception:
        logger.exception('Произошла ошибка:')


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv('DATABASE_PASSWORD')
        database_host = os.getenv('DATABASE_HOST')
        database_port = os.getenv('DATABASE_PORT')
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    env = Env()
    env.read_env()
    tg_token = env('TG_TOKEN')
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    motlin_client_secret = env('MOLTIN_CLIENT_SECRET')
    tg_chat_id = env('TG_CHAT_ID')
    bot = telegram.Bot(token=tg_token)
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot, tg_chat_id))
    logger.info('Бот для логов запущен')

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    while True:

        try:
            dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
            dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
            dispatcher.add_handler(CommandHandler('start', handle_users_reply))
            updater.dispatcher.add_handler(CallbackQueryHandler(handle_menu))
            updater.start_polling()
            logger.info('TG бот запущен')
            updater.idle()

        except Exception:
            logger.exception('Произошла ошибка:')
