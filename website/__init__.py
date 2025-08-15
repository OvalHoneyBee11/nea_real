from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app_root = "/home/lawrence/git/nea_real"
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "keen"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app_root}/{DB_NAME}"
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")

    return app
