import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    current_plant_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    plants = orm.relation("PlantedPlant", back_populates='user')

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
