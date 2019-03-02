# user/views.py
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, jwt_optional, create_access_token, current_user
from flask import jsonify, json, render_template, flash, redirect, request

from app.extensions import db
from .forms import RegisterForm, LoginForm
from .models import User

blueprint = Blueprint('user', __name__)

@blueprint.route('/users/signup', methods=('POST',))
def register_user():

    form = RegisterForm()
    
    user = User(username=form.username.data, email=form.email.data, password=form.password.data, school=form.school.data)
    #user.token = create_access_token(identity=user) TODO: ADD TOKEN

    db.session.add(user)
    db.session.commit()
    return jsonify("true")

    #return json.dumps({'success':False}), 200, {'ContentType':'application/json'}

@blueprint.route('/users/login', methods=('POST',))
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}'.format(
            form.username.data))
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    return json.dumps({'success':False}), 500, {'ContentType':'application/json'} 
