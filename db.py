from data import db_session
from data.users import User
from data.garden import PlantedPlant


class DB:
    @staticmethod
    def add(obj, name, *others):
        if obj == "plant":
            plant = PlantedPlant(name=name, growth_param=0, user_id=others[0], plant_id=others[1])
            db_sess = db_session.create_session()
            db_sess.add(plant)
            db_sess.commit()

        elif obj == "user":
            user = User()
            user.login = name
            user.hashed_password = others[0]
            user.current_plant_id = None

            db_sess = db_session.create_session()
            db_sess.add(user)
            db_sess.commit()

    @staticmethod
    def update(obj):
        if obj == "plant":
            pass

    @staticmethod
    def query():
        pass
        # Нет смысла писать, используется напрямую через sqlalchemy
