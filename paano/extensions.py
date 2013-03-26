from flask_googlelogin import GoogleLogin
from flask_sqlalchemy import SQLAlchemy


login = GoogleLogin()
db = SQLAlchemy()


def init(app):
    login.init_app(app)
    db.init_app(app)
