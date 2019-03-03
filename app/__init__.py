from flask import Flask
from config import Config
from app.extensions import db, migrate, cache, cors, jwt

from app.user.models import User
from app import user

POSTGRES = {
    'user': 'zack',
    'pw': 'password',
    'db': 'mydb',
    'host': 'localhost',
    'port': '5432',
}

# if __name__ == '__main__':
    
#     app.run(debug=True)    

def create_app():
    app = Flask(__name__)
    origins = app.config.get('CORS_ORIGIN_WHITELIST', '*')
    app.config.from_object(Config)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
    %(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

    register_extensions(app, db)
    register_blueprints(app)
    return app

def register_extensions(app, db):
    """Register Flask extensions."""
    #cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    #jwt.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    origins = app.config.get('CORS_ORIGIN_WHITELIST', '*')
    cors.init_app(user.views.blueprint, origins=origins)
    app.register_blueprint(user.views.blueprint)

def jwt_identity(payload):
    return User.get_by_id(payload)

def identity_loader(user):
    return user.id

