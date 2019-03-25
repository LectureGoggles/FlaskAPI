# user/views.py
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, jwt_optional, create_access_token, current_user, get_jwt_identity, jwt_refresh_token_required, create_refresh_token
from flask import jsonify, json, render_template, flash, redirect, request
from flask_login import current_user, login_user, logout_user, login_required
from marshmallow import ValidationError

from app.extensions import db, login_manager, bcrypt
from .forms import RegisterForm, LoginForm
from .models import User
from .schema import UserSchema, user_schema, users_schema

import datetime

blueprint = Blueprint('user', __name__)

@blueprint.route('/users/signup', methods=('POST', ))
def _register_user():

    json_data = request.get_json()
    
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400

    try:
        user_data = user_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    duplicateuser = User.query.filter_by(email=json_data['email'].lower()).first()
    if duplicateuser:
        return jsonify({'message': 'Duplicate user'}), 400

    user = User(
        username=json_data['username'].lower(),
        email=json_data['email'].lower(),
        firstname=json_data['firstname'].lower(),
        lastname=json_data['lastname'].lower(),
        password=bcrypt.generate_password_hash(json_data['password']),
        school=json_data['school'].lower())
    db.session.add(user)
    db.session.commit()
    return jsonify("true")

@blueprint.route('/users/', methods=('GET',))
def _get_user():
    users = User.query.all()
    result = users_schema.dump(users, many=True)
    return jsonify({'users': result})


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
            refresh_token = create_refresh_token(identity=user.username, expires_delta=expires)
            return jsonify(access_token=access_token, refresh_token=refresh_token), 200

    return json.dumps({'Login': False}), 500, {
        'ContentType': 'application/json'
    }

@blueprint.route('/users/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    expires = datetime.timedelta(days=30)
    access_token = create_access_token(identity=current_user, expires_delta=expires)
    return jsonify(ret), 200

@blueprint.route("/users/logout", methods=["GET"])
@jwt_required
def _logout():
    """Logout the current user."""
    #Could use a blacklist to blacklist tokens but for now we'll wait TODO
    user = current_user
    db.session.add(user)
    db.session.commit()
    logout_user()

@blueprint.route("/users/auth", methods=["GET"])
@jwt_optional
def _auth():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
