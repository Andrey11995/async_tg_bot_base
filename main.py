import datetime as dt
import logging
import os
import aiogram.utils.markdown as md
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.executor import start_webhook
from aiogram import Bot, types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT')

TELEGRAM_OWNER_ID = os.getenv('TG_OWNER_ID')
TELEGRAM_ALLOW_IDS = os.getenv('TG_ALLOW_IDS').split(',')


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


class Form(StatesGroup):
    field1_str = State()
    field2_int = State()
    field3_choice = State()
    field4_date = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    """Обработчик команды /start."""
    await message.reply('Welcome!')


@dp.message_handler(commands='some_command')
async def cmd_task(message: types.Message):
    """Обработчик команды /some_command. Инициализация формы."""
    await Form.field1_str.set()
    await message.reply('Input str')


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """Обработчик отмены заполнения формы."""
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Cancelled')


@dp.message_handler(state=Form.field1_str)
async def process_field1_str(message: types.Message, state: FSMContext):
    """Обработчик первого поля field1_str."""
    async with state.proxy() as data:
        data['field1_str'] = message.text
    await Form.next()
    await message.reply('Input int')


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.field2_int)
async def incorrect_int(message: types.Message):
    """Обработчик при неверном вводе значения int."""
    return await message.reply('Validation error! Input int')


@dp.message_handler(state=Form.field2_int)
async def process_field2_int(message: types.Message, state: FSMContext):
    """Обработчик поля field2_int. Вывод кнопок для следующего поля."""
    await state.update_data(field2_int=message.text)
    await Form.next()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Select 1', 'Select 2')
    markup.add('Select 3')
    await message.reply('Select a value', reply_markup=markup)


@dp.message_handler(state=Form.field3_choice)
async def process_field3_choice(message: types.Message, state: FSMContext):
    """Обработчик поля field3_choice. Удаление кнопок."""
    await state.update_data(field3_choice=message.text)
    await Form.next()
    markup = types.ReplyKeyboardRemove()
    # календарь выводится, но бот не реагирует на нажатия
    # datepicker = Datepicker(DatepickerSettings())
    # markup = datepicker.start_calendar()
    # await message.answer('Select date', reply_markup=markup)
    # временно используется текстовый ввод даты с валидацией
    await message.reply('Input date', reply_markup=markup)


async def validate_date(message):
    """Валидатор даты."""
    try:
        return not dt.datetime.strptime(message.text, '%d.%m.%Y')
    except ValueError:
        return True


@dp.message_handler(validate_date, state=Form.field4_date)
async def incorrect_date(message: types.Message):
    """Обработчик при неверном вводе даты."""
    return await message.reply('Input date in format "DD.MM.YYYY"')


# @dp.callback_query_handler(Datepicker.datepicker_callback.filter(), state=Form.field4_date)
# async def process_datepicker(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
#     """Обработчик поля field4_date с календарем."""
#     datepicker = Datepicker(DatepickerSettings())
#     date = await datepicker.process(callback_query, callback_data)
#     if date:
#         await callback_query.message.answer(date.strftime('%d.%m.%Y'))
#     await callback_query.answer()
#     ...


@dp.message_handler(state=Form.field4_date)
async def process_field4_date(message: types.Message, state: FSMContext):
    """Обработчик поля field4_date. Вывод значений заполненной формы."""
    async with state.proxy() as data:
        data['field4_date'] = message.text
        await message.answer(
            md.text(
                md.text('Author:', md.bold(message.from_user.username)),  # *username*
                md.text('String:', md.code(data['field1_str'])),  # `String`
                md.text('Integer:', data['field2_int']),
                md.text('Choice:', data['field3_choice']),
                md.text('Date:', data['field4_date']),
                sep='\n',
            )
        )
    await state.finish()


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
