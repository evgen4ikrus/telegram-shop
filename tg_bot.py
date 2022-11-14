import os
import logging
import redis
from environs import Env


from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


_database = None
logger = logging.getLogger('tg_bot')


def start(bot, update):
    keyboard = [[InlineKeyboardButton('Option 1', callback_data='1'),
                 InlineKeyboardButton('Option 2', callback_data='2')],
                [InlineKeyboardButton('Option 3', callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='Привет! Нажми на одну из кнопок:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query

    bot.edit_message_text(text='Нажата кнопка: {}'.format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
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
        'BUTTON': button,
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
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    logger.info('TG бот запущен')
    updater.idle()
