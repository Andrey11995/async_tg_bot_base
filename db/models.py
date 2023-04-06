from sqlalchemy import Column, Integer

from db.base import BaseTable


class Model(BaseTable):
    __tablename__ = 'table_name_in_db'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    # fields ...
