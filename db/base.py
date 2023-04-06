import logging

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

from settings import with_session

logger = logging.getLogger(__name__)

metadata = MetaData()
Base = declarative_base()


class BaseTable(Base):
    """
    Абстрактная таблица с базовыми методами.

    При вызове методов сессию передавать не нужно.
    Она передается автоматически при помощи декоратора @with_session.
    """
    __abstract__ = True
    __metadata__ = metadata

    @with_session
    async def save(self, session: AsyncSession):
        async with session.begin():
            session.add(self)

    @classmethod
    @with_session
    async def delete(cls, session: AsyncSession, obj):
        await session.delete(obj)
        await session.commit()

    @classmethod
    async def get(cls, **kwargs):
        return (await cls.filter(**kwargs)).one_or_none()

    @classmethod
    @with_session
    async def filter(cls, session: AsyncSession, **kwargs):
        query = f'SELECT * FROM {cls.__tablename__}'
        conditions = []
        for key, value in kwargs.items():
            conditions.append(f"{key} = '{value}'")
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        return (await session.execute(query)).unique()

    @classmethod
    @with_session
    async def create(cls, session: AsyncSession, **kwargs):
        instance = cls(**kwargs)
        async with session.begin():
            session.add(instance)
        return instance

    @with_session
    async def update(self, session: AsyncSession, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        async with session.begin():
            session.add(self)
