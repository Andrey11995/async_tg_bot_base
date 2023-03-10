import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

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

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    future=True,
    class_=AsyncSession
)

BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
bot['db'] = async_session
dp = Dispatcher(bot, storage=storage)

WEBHOOK = bool(int(os.getenv('WEBHOOK')))
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PREFIX = os.getenv('WEBHOOK_PREFIX')
WEBHOOK_PATH = f'/{WEBHOOK_PREFIX}/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT')


def get_session():
    return async_session()
