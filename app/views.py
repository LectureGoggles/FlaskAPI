# ourapp/views.py
from app import app
from app.forms import RegisterForm, LoginForm
from app.models import User
from app.__init__ import db
from flask import jsonify, json, render_template, flash, redirect, request


@app.route('/')
def hello():
    return "Hello"

@app.route('/index')
def home():
    return "Home"

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    #if form.validate_on_submit():
    if request.method == "POST":
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=form.password.data, school=form.school.data)
        db.session.add(user)
        db.session.commit()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    #return render_template('signup.html', form=form)