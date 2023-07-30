from aiogram.utils.executor import start_polling, start_webhook

from db.base import Base
from handlers import init_handlers
from settings import *

logger = logging.getLogger(__name__)


async def on_startup_webhook(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    # создание таблиц при запуске бота
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def on_startup_polling(dispatcher):
    # создание таблиц при запуске бота
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def on_shutdown_webhook(dispatcher):
    await bot.delete_webhook()


if __name__ == '__main__':
    init_handlers(dp)
    logger.info('Bot started')
    if WEBHOOK:
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            skip_updates=True,
            on_startup=on_startup_webhook,
            on_shutdown=on_shutdown_webhook,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    else:
        start_polling(
            dispatcher=dp,
            skip_updates=True,
            on_startup=on_startup_polling
        )
