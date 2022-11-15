import logging
import os

import redis
from environs import Env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

from format_message import create_product_description
from moltin_helpers import (get_all_products, get_file_by_id,
                            get_moltin_access_token, get_product_by_id,
                            get_product_files)

_database = None
logger = logging.getLogger('tg_bot')


def start(bot, update):
    moltin_access_token = get_moltin_access_token(moltin_client_id, motlin_client_secret)
    products = get_all_products(moltin_access_token)
    keyboard = [
        [InlineKeyboardButton(product['attributes']['name'], callback_data=product['id'])] for product in products
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='Привет! Нажми на одну из кнопок:', reply_markup=reply_markup)
    return 'HANDLE_MENU'


def handle_menu(bot, update):
    moltin_access_token = get_moltin_access_token(moltin_client_id, motlin_client_secret)
    query = update.callback_query
    product_id = '{}'.format(query.data)
    product = get_product_by_id(moltin_access_token, product_id)
    message = create_product_description(product)
    product_files = get_product_files(moltin_access_token, product_id)
    if product_files:
        file_id = product_files[0].get('id')
        file = get_file_by_id(moltin_access_token, file_id)
        file_link = file.get('link').get('href')
        bot.send_photo(chat_id=query.message.chat_id, caption=message, photo=file_link)
        bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        return 'START'
    bot.send_message(text=message, chat_id=query.message.chat_id)
    return 'START'


def echo(bot, update):
    users_reply = update.message.text
    update.message.reply_text(users_reply)
    return 'ECHO'


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
        'ECHO': echo
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
    token = env('TG_TOKEN')
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    motlin_client_secret = env('MOLTIN_CLIENT_SECRET')
    moltin_access_token = get_moltin_access_token(moltin_client_id, motlin_client_secret)

    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.dispatcher.add_handler(CallbackQueryHandler(handle_menu))
    updater.start_polling()
    logger.info('TG бот запущен')
    updater.idle()
