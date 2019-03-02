# ourapp/views.py
from app import app
from app.forms import RegisterForm, LoginForm
from app.models import User
from app.__init__ import db
from flask import jsonify, json, render_template, flash, redirect, request


@app.route('/subject/create', methods=['GET', 'POST'])
@login_required
def subjectcreate()
    form = SubjectCreation()
    if form.validate_on_submit():
        if request.method == "POST":
            subject = Subject(subject=form.subject.data, )