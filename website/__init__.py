from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app_root = "."
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "keen"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app_root}/{DB_NAME}"
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .tests import tests
    from .sn import sn
    from .simulator import sim
    from .class_info import cls

    app.register_blueprint(sim, url_prefix="/sim")
    app.register_blueprint(cls, url_prefix="/cls")
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(tests, url_prefix="/tests")
    app.register_blueprint(sn, url_prefix="/sn")

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()

