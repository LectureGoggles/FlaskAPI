from flask import Blueprint, request, redirect
from flask_jwt_extended import jwt_required, jwt_optional, create_access_token, get_jwt_identity
from flask import jsonify, json, render_template, flash, redirect, request

from app.extensions import db, login_manager, bcrypt
from .forms import SubjectCreation, TopicCreation, PostCreation
from .models import Subject, Topic, Post
from app.user.models import User

blueprint = Blueprint('post', __name__)

### SUBJECT
@blueprint.route('/subject/create', methods=['POST',])
@jwt_required
def _subjectcreate():
    form = SubjectCreation()
    current_user = get_jwt_identity()

    # check for subject already created
    duplicatesubject = Subject.query.filter_by(subject=form.subject.data.lower()).first()
    if duplicatesubject:
        return jsonify(success='False', code=400, description='duplicate subject')

    # Check to see if subject exists
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        subject = Subject(
            subject=form.subject.data.lower(),
            description=form.description.data,
            author_id=user.id
        )
        db.session.add(subject)
        db.session.commit()
        return jsonify(success='True', code=200)
    
    return jsonify(success='False', code=400)

@blueprint.route('/subject/search/<subjectstr>', methods=['GET',])
def _getsubject(subjectstr):
    getsubject = Subject.query.filter_by(subject=subjectstr.lower()).first()

    if getsubject:
        return jsonify(subject_id=getsubject.id, subject_name=getsubject.subject, subject_description=getsubject.description, success='True', code=200)
    else:
        return jsonify(success='False', code=400, description='subject does not exist')


### POST
@blueprint.route('/<int:topicid>/post/create', methods=['POST',])
@jwt_required
def _postcreate(topicid):
    form = PostCreation()
    current_user = get_jwt_identity()

    duplicatepost = Post.query.filter_by(subject=form.subject.data).first()
    if duplicatepost:
        return jsonify(success='False', code=400, description='duplicate subject')

    #is this a valid subject
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        post = Post(
            subject = form.subject.data,
            description = form.description.data,
            author_id = user.id,
            topic_id = topicid,
        )
        db.session.add(post)
        db.session.commit()
        return jsonify(sucess='True', code=200)

    return jsonify(success='False', code=200)

### TOPIC
@blueprint.route('/<int:subjectid>/topic/create', methods=['POST',])
@jwt_required
def _posttopic(subjectid):
    form = TopicCreation()
    current_user = get_jwt_identity()

    duplicatetopic = Topic.query.filter_by(subject=form.subject.data).first()
    if duplicatetopic:
        return jsonify(success='False', code=400, description='duplicate subject')

    #is this a valid subject
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        topic = Topic(
            subject = form.subject.data,
            description = form.description.data,
            author_id = user.id,
            subject_id = subjectid
        )
        db.session.add(topic)
        db.session.commit()
        return jsonify(sucess='True', code=200)

    return jsonify(success='False', code=200)

# NOTES
# TODO(zack)
# _postcreate(subjectid)
# Relation to the subject is posted to but not sure if we'll need to add
# children to the subject itself.
