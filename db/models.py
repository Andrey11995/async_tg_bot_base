from sqlalchemy import BigInteger, Column, String

from db.base import BaseTable


class Model(BaseTable):
    __tablename__ = 'table_name_in_db'

    id = Column(BigInteger, autoincrement=True, primary_key=True)
    user_tg_id = Column(BigInteger, index=True, nullable=False)
    text = Column(String(100), nullable=False)
    # other fields ...
