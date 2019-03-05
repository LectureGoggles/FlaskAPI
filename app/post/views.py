from flask import Blueprint, request
from flask_jwt_extended import jwt_required, jwt_optional, create_access_token, current_user
from flask import jsonify, json, render_template, flash, redirect, request
# TODO(zack): remove in future if not used
from flask_login import current_user, login_user, logout_user, login_required

from app.extensions import db, login_manager, bcrypt
from .forms import ResourceCreation, SubjectCreation
from .models import Subject, Resource

blueprint = Blueprint('post', __name__)

@blueprint.route('/subject/create', methods=['GET', 'POST'])
def _subjectcreate():
    form = SubjectCreation()
    # TODO(zack): implement