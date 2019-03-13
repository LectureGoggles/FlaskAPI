from flask_sqlalchemy import SQLAlchemy
from app.extensions import db
import datetime as dt

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer)
    subject = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    # Relation with topic
    addresses = db.relationship('Topic', backref='subjects', lazy=True)

class Topic(db.Model):
    __tablename__= 'topics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer)
    subject = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)

    # Relation with subject and post
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    posts = db.relationship('Post', backref='topics', lazy=True)
    

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(50), nullable=False)
    author_id = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    upvote = db.Column(db.Integer, default=0) # TODO(zack): Replace with upvote database model
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    # Relation with topic
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)