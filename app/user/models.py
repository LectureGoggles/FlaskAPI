from flask_sqlalchemy import SQLAlchemy
from app.extensions import db
import datetime as dt
from flask_login import UserMixin


class User(UserMixin, db.Model):

    __tablename__ = 'users'

    # Create a model of a user who is signing up for an account.
    # This user should have a unique username and email.
    # Their password will need to be hashed.
    # Use a boolean is_active and is_staff for determining if user has been banned and is_staff for more access later.
    # Also basic created_at to determine creation date.
    # To determine if changes have been made to the account use updated_at
    # The university they attend or (school)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(
        db.Binary(60), nullable=False)  #TODO(zack): Add hashed/salt password
    school = db.Column(db.String(80), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_staff = db.Column(db.Boolean, default=False)

    def __init__(self, username, email, password, school):
        self.username = username
        self.email = email
        self.password = password
        self.school = school

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __repr__(self):
        return '<User %r>' % self.email