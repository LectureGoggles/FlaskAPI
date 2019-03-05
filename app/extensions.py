from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
cors = CORS()
jwt = JWTManager()
bcrypt = Bcrypt()
login_manager = LoginManager()