from flask import Flask
from config import Config
from app.extensions import db, migrate, cache, cors, jwt, login_manager, bcrypt, ma

from app.user.models import User
from app import user, post

POSTGRES = {
    'user': 'admin',
    'pw': 'password',
    'db': 'mydb1',
    'host': '127.0.0.1',
    'port': '5432',
}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['DEBUG'] = False

    # Using an internal ip 10.0.3.4
    # Database
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

    # Function calls
    register_extensions(app, db)
    register_blueprints(app)

    return app


def register_extensions(app, db):
    """Register Flask extensions."""
    #cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    origins = app.config.get('CORS_ORIGIN_WHITELIST', '*')
    cors.init_app(user.views.blueprint, origins=origins)
    cors.init_app(post.views.blueprint, origins=origins)
    app.register_blueprint(post.views.blueprint)
    app.register_blueprint(user.views.blueprint)
