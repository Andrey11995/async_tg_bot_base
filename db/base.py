import logging

from sqlalchemy import select, MetaData
from sqlalchemy.orm import declarative_base

from settings import get_session

logger = logging.getLogger(__name__)

metadata = MetaData()
Base = declarative_base()


class BaseTable(Base):
    """
    Абстрактная таблица с базовыми методами.

    Также можно получать сессию из присланного боту сообщения:
    message.bot.get('db')
    """
    __abstract__ = True
    __metadata__ = metadata

    @staticmethod
    async def execute(query):
        async with get_session() as session:
            return await session.execute(query)

    @staticmethod
    async def scalar(query):
        async with get_session() as session:
            return await session.scalar(query)

    async def save(self):
        async with get_session() as session:
            await session.merge(self)
            await session.commit()

    async def create(self):
        await self.save()

    async def update(self, **kwargs):
        for field, value in kwargs.items():
            old_value = getattr(self, field)
            if isinstance(value, dict) and isinstance(old_value, dict):
                old_value.update(value)
                value = old_value
            setattr(self, field, value)
        await self.save()

    async def delete(self):
        async with get_session() as session:
            await session.delete(self)
            await session.commit()

    @classmethod
    async def delete_list(cls, **kwargs):
        for item in await cls.list(**kwargs):
            await item.delete()

    @classmethod
    async def count(cls, **kwargs):
        return (await cls.execute(await cls.query(kwargs))).scalar_one_or_none().count()

    @classmethod
    async def exists(cls, **kwargs):
        return bool((await cls.execute(select(cls).filter_by(**kwargs))).scalar_one_or_none())

    @classmethod
    async def query(cls, kwargs):
        if kwargs:
            return select(cls).filter_by(**kwargs)
        return select(cls)

    @classmethod
    async def get(cls, **kwargs):
        return (await cls.execute(select(cls).filter_by(**kwargs))).scalars().unique().one_or_none()

    @classmethod
    async def list(cls, **kwargs):
        return (await cls.execute(await cls.query(kwargs))).scalars().unique().all()
