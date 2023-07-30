import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

logging.basicConfig(level=logging.INFO)

DB_HOST = os.getenv('POSTGRES_HOST')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')

engine = create_async_engine(
    f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}',
    future=True,
    echo=True
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    future=True
)

BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

WEBHOOK = bool(int(os.getenv('WEBHOOK')))
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PREFIX = os.getenv('WEBHOOK_PREFIX')
WEBHOOK_PATH = f'/{WEBHOOK_PREFIX}/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT')


def with_session(method):
    async def wrapper(cls, session=None, *args, **kwargs):
        if session:
            return await method(cls, session, *args, **kwargs)
        async with async_session() as session:
            return await method(cls, session, *args, **kwargs)
    return wrapper
