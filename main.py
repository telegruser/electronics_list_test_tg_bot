import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.utils.exceptions import MessageToDeleteNotFound

import util


logger = util.init_logger(__name__)

API_TOKEN = os.environ.get('API_TOKEN')
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST', '')
WEBHOOK_PATH = '/' + API_TOKEN
WEBHOOK_URL = WEBHOOK_HOST + API_TOKEN
LOCAL_MODE = bool(int(os.environ.get('LOCAL_MODE', '0')))
CONNECTION_TYPE = os.environ.get('CONNECTION_TYPE', None)

if not CONNECTION_TYPE:
    CONNECTION_TYPE = 'polling' if LOCAL_MODE else 'webhook'
PROXY = os.environ.get('PROXY', 'socks5://127.0.0.1:9150')

bot = Bot(API_TOKEN, proxy=PROXY) if LOCAL_MODE else Bot(API_TOKEN)
dispatcher = Dispatcher(bot)


async def send_start_message(user_id):
    await bot.send_message(
        user_id,
        util.get_time_welcome(),
        reply_markup=InlineKeyboardMarkup()
            .add(InlineKeyboardButton('Список производителей электроники:', callback_data='get_electronics_list'))
    )


@dispatcher.message_handler(commands='start')
async def cmd_start(message: Message):
    logger.info(f'User {message.from_user.id} -> "{message.text}"')
    await send_start_message(message.from_user.id)


@dispatcher.callback_query_handler(lambda callback_query: callback_query.data.startswith('get_electronics_list'))
async def cq_get_list(callback_query: CallbackQuery):
    logger.info(f'User {callback_query.from_user.id} -> CallbackQuery: "{callback_query.data}"')
    await callback_query.answer()
    try:
        await callback_query.message.delete()
    except MessageToDeleteNotFound:
        pass
    await bot.send_message(
        callback_query.from_user.id,
        'Список производителей электроники:',
        reply_markup=util.make_pagnation_keyboard('get_pag_electronics_list', util.electronics_list_formated)
    )


@dispatcher.callback_query_handler(lambda callback_query: callback_query.data.startswith('get_pag_electronics_list'))
async def cq_get_pag_list(callback_query: CallbackQuery):
    logger.info(f'User {callback_query.from_user.id} -> CallbackQuery: "{callback_query.data}"')
    await callback_query.answer()

    full_query = callback_query.data.split(':')
    query = full_query[1]
    param = full_query[2] if len(full_query) > 2 else None

    if query == 'get':
        num = int(param)
        await callback_query.message.edit_reply_markup(
            util.make_pagnation_keyboard('get_pag_electronics_list', util.electronics_list_formated, num))

    elif query == 'to_start':
        try:
            await callback_query.message.delete()
        except MessageToDeleteNotFound:
            pass
        await send_start_message(callback_query.from_user.id)

    elif query == 'select':
        # код при выборе поставщика
        pass


if __name__ == '__main__':
    logger.info('Starting..')

    if CONNECTION_TYPE == 'polling':
        logger.info('Connection mode: polling.')
        executor.start_polling(dispatcher, skip_updates=True)

    elif CONNECTION_TYPE == 'webhook':
        logger.info('Connection mode: webhook.')
        await bot.delete_webhook()
        await bot.set_webhook(WEBHOOK_URL)
        executor.start_webhook(
            dispatcher=dispatcher,
            webhook_path=WEBHOOK_PATH,
            skip_updates=True,
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000))
        )
