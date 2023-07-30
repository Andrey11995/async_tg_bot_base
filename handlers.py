import aiogram.utils.markdown as md
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from db.models import Model
from forms import Form


def init_handlers(dp):
    @dp.message_handler(commands='start')
    async def cmd_start(message: types.Message):
        """Обработчик команды /start."""
        await message.answer('Welcome!')

    @dp.message_handler(
        lambda message: len(message.text) < 100,
        content_types=types.ContentTypes.TEXT
    )
    async def text_handler(message: types.Message):
        # пример работы с базой данных
        model = await Model.create(
            user_tg_id=message.from_user.id,
            text=message.text
        )
        await message.answer(f'Created! Text: {model.text}')

    @dp.message_handler(
        lambda message: message.voice.duration < 60,
        content_types=types.ContentTypes.VOICE
    )
    async def voice_handler(message: types.Message):
        pass

    @dp.message_handler(content_types=types.ContentTypes.PHOTO)
    async def photo_handler(message: types.Message):
        pass

    @dp.message_handler(content_types=types.ContentTypes.VIDEO)
    async def video_handler(message: types.Message):
        pass

    @dp.message_handler(content_types=types.ContentTypes.DOCUMENT)
    async def document_handler(message: types.Message):
        pass

    # Обработчики формы
    @dp.message_handler(commands='init_form')
    async def cmd_init_form(message: types.Message):
        """Обработчик команды /init_form. Инициализация формы."""
        await Form.field1_str.set()
        await message.reply('Input str')

    @dp.message_handler(state='*', commands='cancel')
    @dp.message_handler(
        Text(equals=['Cancel', 'cancel'], ignore_case=True), state='*'
    )
    async def cancel_handler(message: types.Message, state: FSMContext):
        """Обработчик отмены заполнения формы."""
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
        """Обработчик поля field3_choice. Вывод значений заполненной формы."""
        async with state.proxy() as data:
            data['field3_choice'] = message.text
            await message.answer(
                md.text(
                    md.text('Author:', md.bold(message.from_user.username)),  # *username*
                    md.text('String:', md.code(data['field1_str'])),  # `String`
                    md.text('Integer:', data['field2_int']),
                    md.text('Choice:', data['field3_choice']),
                    sep='\n',
                )
            )
        await state.finish()
