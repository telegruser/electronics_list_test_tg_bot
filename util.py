import logging
import sys
from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


electronics_list = ['Apple', 'Samsung', 'Nokia', 'Sony', 'Canon', 'Panasonic', 'Bose', 'Microsoft', 'LG', 'Intel',
                    'Nvidia', 'Dell', 'IBM', 'Acer', 'Asus', 'Lenovo', 'Xiaomi', 'Huawei']
electronics_list_formated = electronics_list.copy()
electronics_list_formated.sort()
electronics_list_formated = [f'{i+1}. {item}' for i, item in enumerate(electronics_list_formated)]


def make_pagnation_keyboard(query_prefix, source, start=0, count=10):
    keyboard = InlineKeyboardMarkup(row_width=3)
    end = start + count

    for i in range(min(count, len(source)-start)):
        n = i + start
        keyboard.add(InlineKeyboardButton(source[n], callback_data=f'{query_prefix}:select:{n}'))

    keyboard.add(InlineKeyboardButton('Назад', callback_data=f'{query_prefix}:to_start'))

    if start > 0:
        keyboard.insert(InlineKeyboardButton('<<', callback_data=f'{query_prefix}:get:{max(start-count, 0)}'))

    if len(source) > end:  # если не последняя страница
        keyboard.insert(InlineKeyboardButton('>>', callback_data=f'{query_prefix}:get:{end}'))

    return keyboard


times = (
    'Доброй ночи!',   # 00:00 - 06:00
    'Доброе утро!',   # 06:00 - 12:00
    'Добрый день!',   # 12:00 - 18:00
    'Добрый вечер!',  # 18:00 - 00:00
)


def get_time_welcome() -> str:
    return times[datetime.now().hour // 6]


def init_logger(name, debug=False) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    console_output_handler = logging.StreamHandler(sys.stderr)
    console_output_handler.setFormatter(formatter)
    logger.addHandler(console_output_handler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    return logger
