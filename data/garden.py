import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class PlantedPlant(SqlAlchemyBase):
    __tablename__ = 'garden'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    growth_param = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    plant_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("plants.id"))
    plant = orm.relation('Plant')
