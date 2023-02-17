import datetime as dt
import io

import aiogram.utils.markdown as md

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.executor import start_polling, start_webhook
from aiogram import types

from db.base import Base
from file_handlers import process_excel_handler, process_file_handler
from settings import *

logger = logging.getLogger(__name__)


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    # создание таблиц при запуске бота
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


class Form(StatesGroup):
    """Форма с разными типами данных."""
    field1_str = State()
    field2_int = State()
    field3_choice = State()
    field4_date = State()


class ExcelForm(StatesGroup):
    """Форма загрузки excel таблицы."""
    file = State()


class TextFileForm(StatesGroup):
    """Форма загрузки текстового файла."""
    action = State()
    file = State()


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
@dp.message_handler(
    Text(equals=['Cancel', 'cancel'], ignore_case=True), state='*'
)
async def cancel_handler(message: types.Message, state: FSMContext):
    """Обработчик отмены заполнения форм."""
    current_state = await state.get_state()
    if not current_state:
        return
    await state.finish()
    markup = types.ReplyKeyboardRemove()
    await message.reply('Cancelled', reply_markup=markup)


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


@dp.message_handler(commands='upload_excel')
async def cmd_upload_excel(message: types.Message):
    """Обработчик команды /upload_excel. Инициализация формы."""
    await ExcelForm.file.set()
    await message.reply('Upload excel:')


@dp.message_handler(
    state=ExcelForm.file, content_types=types.ContentTypes.DOCUMENT
)
async def process_excel(message: types.Message, state: FSMContext):
    """Обработчик отправленной excel таблицы."""
    extension = message.document.file_name.split('.')[-1]
    if extension in ['xls', 'xlsx']:
        output = io.BytesIO()
        excel = await message.document.download(destination_file=output)
        new_excel = await process_excel_handler(excel)
        await message.reply_document(
            ('excel_name.xlsx', new_excel),
            caption='Success'
        )
    else:
        await message.reply('Incorrect excel')
    await state.finish()


@dp.message_handler(commands='upload_file')
async def cmd_upload_file(message: types.Message):
    """Обработчик команды /upload_file. Инициализация формы."""
    await TextFileForm.action.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Process file')
    markup.add('Cancel')
    await message.reply('Choose action:', reply_markup=markup)


@dp.message_handler(state=TextFileForm.action)
async def process_file_action(message: types.Message, state: FSMContext):
    """
    Обработчик выбранного действия.
    Можно дополнить переключением на другое состояние
    в зависимости от действия.
    """
    choice = message.text
    if choice == 'Process file':
        await state.update_data(action=message.text)
        markup = types.ReplyKeyboardRemove()
        await TextFileForm.file.set()
        await message.reply('Upload file:', reply_markup=markup)
    else:
        await message.reply('Incorrect action')
        await state.finish()


@dp.message_handler(
    state=TextFileForm.file, content_types=types.ContentTypes.DOCUMENT
)
async def process_file(message: types.Message, state: FSMContext):
    """Обработчик отправленного текстового файла."""
    async with state.proxy() as data:
        action = data['action']
    extension = message.document.file_name.split('.')[-1]
    if extension == 'txt':
        output = io.BytesIO()
        if action == 'Process file':
            file = await message.document.download(destination_file=output)
            # делю файл по строкам для удобства
            new_file = await process_file_handler(file.readlines())
            await message.reply_document(
                (f'new_file.txt', new_file),
                caption='Success'
            )
        elif action == 'Other action':
            pass
        else:
            await message.reply('Action not found')
    else:
        await message.reply('Incorrect text file')
    await state.finish()


if __name__ == '__main__':
    logger.info('Bot started')
    if WEBHOOK:
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    else:
        start_polling(
            dispatcher=dp,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown
        )
