# user/views.py
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, jwt_optional, create_access_token, current_user, get_jwt_identity
from flask import jsonify, json, render_template, flash, redirect, request
from flask_login import current_user, login_user, logout_user, login_required

from app.extensions import db, login_manager, bcrypt
from .forms import RegisterForm, LoginForm
from .models import User

import datetime

blueprint = Blueprint('user', __name__)

@blueprint.route('/users/signup', methods=('POST', ))
def _register_user():

    form = RegisterForm()
    duplicateuser = User.query.filter_by(email=form.email.data).first()
    if duplicateuser:
        return jsonify(success='False', code=400)

    user = User(
        username=form.username.data,
        email=form.email.data,
        password=bcrypt.generate_password_hash(form.password.data),
        school=form.school.data)
    db.session.add(user)
    db.session.commit()
    return jsonify("true")


@blueprint.route('/users/login', methods=('POST', ))
def _login_user():
    form = LoginForm()
    user = User.query.filter_by(email=form.email.data).first()
    if user:
        if bcrypt.check_password_hash(user.password, form.password.data):
            # authenticate user and resave into db
            db.session.add(user)
            db.session.commit()
            flash('Login requested for user {}'.format(user.email))
            expires = datetime.timedelta(days=30)
            access_token = create_access_token(
                identity=user.username, expires_delta=expires)  # Create access token for user
            return jsonify(access_token=access_token), 200

    return json.dumps({'Login': False}), 500, {
        'ContentType': 'application/json'
    }


@blueprint.route("/users/logout", methods=["GET"])
def _logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()


@blueprint.route("/users/auth", methods=["GET"])
@jwt_optional
def _auth():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
