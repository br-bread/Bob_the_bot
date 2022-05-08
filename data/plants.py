import sqlalchemy
from .db_session import SqlAlchemyBase


class Plant(SqlAlchemyBase):
    __tablename__ = 'plants'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    latin_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)


