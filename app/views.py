# ourapp/views.py
from app import app
from app.forms import RegisterForm, LoginForm
from app.models import User
from app.__init__ import db
from flask import jsonify, json, render_template, flash, redirect, request
