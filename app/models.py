from flask_sqlalchemy import SQLAlchemy
from app import db
import datetime

# class BaseModel(db.Model):
#     """Base data model for all objects"""
#     __abstract__ = True

#     def __init__(self, *args):
#         super().__init__(*args)

#     def __repr__(self):
#         """Define a base way to print models"""
#         return '%s(%s)' % (self.__class__.__name__, {
#             column: value
#             for column, value in self._to_dict().items()
#         })

#     def json(self):
#         """
#                 Define a base way to jsonify models, dealing with datetime objects
#         """
#         return {
#             column: value if not isinstance(value, datetime.date) else value.strftime('%Y-%m-%d')
#             for column, value in self._to_dict().items()
#         }

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False) # TODO: Needs to be deleted in favor of hashed password
    school = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_staff = db.Column(db.Boolean, default=False)

    def __init__(self, first_name, last_name, email, password, school):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.school = school
    
    def __repr__(self):
        return '<User %r>' % self.email
