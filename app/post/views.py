from flask import Blueprint, request
from flask_jwt_extended import jwt_required, jwt_optional, create_access_token, get_jwt_identity
from flask import jsonify, json, render_template, flash, redirect, request

from app.extensions import db, login_manager, bcrypt
from .forms import ResourceCreation, SubjectCreation
from .models import Subject, Resource

blueprint = Blueprint('post', __name__)

@blueprint.route('/subject/create', methods=['POST',])
@jwt_required
def _subjectcreate():
    form = SubjectCreation()

    current_user = get_jwt_identity()

    
    # TODO(zack): implement