from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

from db.base import BaseTable


class Model(BaseTable):
    __tablename__ = 'table_name_in_db'

    str_field = Column(String, primary_key=True, unique=True)
    jsonb_field = Column(JSONB)
