from app.extensions import db
import datetime as dt
from flask_login import UserMixin


class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    password = db.Column(db.Binary(60), nullable=False)
    school = db.Column(db.String(80), nullable=False)
    profile_image = db.Column(db.String(2084), nullable=False, default="Avatar.svg")
    created_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_teacher = db.Column(db.Boolean, default=False)
    is_staff = db.Column(db.Boolean, default=False)

    subject_subscriptions = db.relationship('Subject_Subscription', backref='users', lazy=True)
    topic_subscriptions = db.relationship('Topic_Subscription', backref='users', lazy=True)

    def __init__(self, username, email, firstname, lastname, password, school):
        self.username = username
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.school = school

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def __repr__(self):
        return '<User %r>' % self.email


class Subject_Subscription(db.Model):
    __tablename__ = 'subject_subscription'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, nullable=False)


class Topic_Subscription(db.Model):
    __tablename__ = 'topic_subscription'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, nullable=False)
