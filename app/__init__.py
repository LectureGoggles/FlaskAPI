from flask import Flask, request, url_for
from config import Config
from app.extensions import db, migrate, cache, cors, jwt, login_manager, bcrypt, ma

from app.user.models import User
from app.user.views import userblueprint
from app.post.views import postblueprint
from os.path import join, dirname, realpath
import os

DB_INFO = {
    'user': os.environ["db_username"],
    'pw': os.environ["db_passwd"],
    'db': os.environ["db_name"],
    'host': os.environ["db_host"],
    'port': os.environ["db_port"],
}

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'image_folder/')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['DEBUG'] = False

    # Database
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % DB_INFO

    # Function calls
    register_extensions(app, db)
    register_blueprints(app)

    return app


def register_extensions(app, db):
    """Register Flask extensions."""
    # cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    origins = app.config.get('CORS_ORIGIN_WHITELIST', '*')
    cors.init_app(userblueprint, origins=origins)
    cors.init_app(postblueprint, origins=origins)
    app.register_blueprint(postblueprint)
    app.register_blueprint(userblueprint)
