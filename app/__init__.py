from app.models import db
from config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

from app import views

POSTGRES = {
    'user': 'zack',
    'pw': 'password',
    'db': 'my_database',
    'host': 'localhost',
    'port': '5432',
}
    
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
db.init_app(app)

if __name__ == '__main__':
    
    app.run(debug=True)