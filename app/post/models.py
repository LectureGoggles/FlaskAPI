from flask_sqlalchemy import SQLAlchemy
from app.extensions import db
import datetime as dt

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(50), nullable=False)
    author_id = db.Column(db.Integer) # TODO(zack): , db.ForeignKey('user.id')
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)


class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(50), nullable=False)
    author_id = db.Column(db.Integer) # TODO(zack): , db.ForeignKey('user.id')
    author = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    upvote = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)