# user/views.py
from flask import Blueprint, request, url_for, send_file, jsonify, json, render_template, flash, redirect, send_from_directory
from flask_jwt_extended import jwt_required, jwt_optional, create_access_token, current_user, get_jwt_identity, jwt_refresh_token_required, create_refresh_token
from flask_login import current_user, login_user, logout_user, login_required
from marshmallow import ValidationError
from werkzeug.utils import secure_filename

from app.extensions import db, login_manager, bcrypt
from .forms import RegisterForm, LoginForm
from .models import User
from .schema import UserSchema, user_schema, users_schema
import os
from os.path import realpath
import datetime

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

userblueprint = Blueprint('user', __name__)

@userblueprint.route('/v1/users/signup', methods=('POST', ))
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

@userblueprint.route('/users/', methods=('GET',))
def _get_user():
    users = User.query.all()
    result = users_schema.dump(users, many=True)
    return jsonify({'users': result})


@userblueprint.route('/v1/users/login', methods=('POST', ))
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

@userblueprint.route('/v1/users/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    expires = datetime.timedelta(days=30)
    access_token = create_access_token(identity=current_user, expires_delta=expires)
    return jsonify(access_token=access_token), 200

@userblueprint.route("/v1/users/logout", methods=["GET"])
@jwt_required
def _logout():
    """Logout the current user."""
    #Could use a blacklist to blacklist tokens but for now we'll wait TODO
    user = current_user
    db.session.add(user)
    db.session.commit()
    logout_user()

@userblueprint.route("/v1/users/auth", methods=["GET"])
@jwt_optional
def _auth():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@userblueprint.route("/v1/users/setUserImage", methods=["POST"])
@jwt_required
def _set_image():

    current_user = get_jwt_identity()

    if current_user:
        user = User.query.filter_by(username=current_user).first()
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return jsonify({'message': 'No file part'}), 400
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return jsonify({'message': 'No selected file'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join("app/image_folder/", filename.lower()))
            user.profile_image = filename.lower()
            db.session.commit()
            return jsonify({'message': True}), 200

    return json({'message': False}), 400


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@userblueprint.route("/v1/users/getUserImage", methods=["GET"])
@jwt_required
def _get_image():

    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        filename = secure_filename(user.profile_image)
        return send_file(os.path.join("image_folder/", filename))

    return jsonify({'message': "Not a current jwt token"}), 400