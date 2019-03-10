from flask import Blueprint, request, redirect
from flask_jwt_extended import jwt_required, jwt_optional, create_access_token, get_jwt_identity
from flask import jsonify, json, render_template, flash, redirect, request

from app.extensions import db, login_manager, bcrypt
from .forms import ResourceCreation, SubjectCreation
from .models import Subject, Resource
from app.user.models import User

blueprint = Blueprint('post', __name__)

@blueprint.route('/subject/create', methods=['POST',])
@jwt_required
def _subjectcreate():
    form = SubjectCreation()
    current_user = get_jwt_identity()

    # check for subject already created
    duplicatesubject = Subject.query.filter_by(subject=form.subject.data).first()
    if duplicatesubject:
        return jsonify(success='False', code=400, description='duplicate subject')

    # Check to see if subject exists
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        subject = Subject(
            subject=form.subject.data,
            description=form.description.data,
            author_id=user.id
        )
        db.session.add(subject)
        db.session.commit()
        return jsonify(success='True', code=200)
    
    return jsonify(success='False', code=400)

@blueprint.route('/subject/search/<subjectstr>', methods=['GET',])
def _getsubject(subjectstr):
    getsubject = Subject.query.filter_by(subject=subjectstr).first()

    if getsubject:
        return jsonify(subject_id=getsubject.id, subject_name=getsubject.subject, subject_description=getsubject.description, success='True', code=200)
    else:
        return jsonify(success='False', code=400, description='subject does not exist')

@blueprint.route('/<int:subjectid>/post/create')
@jwt_required
def _postcreate(subjectid):
    getsubject = Subject.query.filter_by(id=subjectid).first()
    current_user = get_jwt_identity()

    #is this a valid subject
    if getsubject:
        user = User.query.filter_by(username=current_user).first()
        post = Resource(
            subject = form.subject.data,
            description = form.description.data,
            author_id = current_user.id,
            author = current_user.username,
            relation_id = subjectid
        )
        db.session.add(post)
        db.session.commit()
        return jsonify(sucess='True', code=200)

    return jsonify(success='False', code=200)

# NOTES
# _postcreate(subjectid)
# Relation to the subject is posted to but not sure if we'll need to add
# children to the subject itself.
