from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class LoginForm(FlaskForm):
    email = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class RegisterForm(FlaskForm):
    username = StringField(
        'Username', validators=[DataRequired(),
                                  Length(min=2, max=80)])

    firstname = StringField("First Name", validators=[DataRequired()])
    lastname = StringField("Last Name", validators=[DataRequired()])
    email = StringField(
        'Email', validators=[DataRequired(),
                             Email(),
                             Length(min=6, max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    school = StringField(
        'School', validators=[DataRequired(),
                              Length(min=2, max=80)])
