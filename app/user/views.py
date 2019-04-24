# user/views.py
from flask import Blueprint, request, send_file, jsonify, json, flash
from flask_jwt_extended import jwt_required, jwt_optional, create_access_token, get_jwt_identity, jwt_refresh_token_required, create_refresh_token
from marshmallow import ValidationError
from werkzeug.utils import secure_filename

from app.extensions import db, bcrypt
from .forms import LoginForm
from .models import User, Subject_Subscription, Topic_Subscription
from app.post.models import Subject, Topic
from .schema import UserSchema, user_schema, users_schema
from .schema import SubjectSubscriptionSchema, subject_subscription_schema, subjects_subscription_schema
from .schema import TopicSubscriptionSchema, topic_subscription_schema, topics_subscription_schema

import os
import datetime

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

userblueprint = Blueprint('user', __name__)


@userblueprint.route('/v1/users/signup/', methods=('POST', ))
def _register_user():

    json_data = request.get_json()

    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400

    try:
        user_data = user_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    duplicateuser = User.query.filter_by(
        email=json_data['email'].lower()).first()
    if duplicateuser:
        return jsonify({'message': 'Duplicate user'}), 400

    user = User(username=json_data['username'].lower(),
                email=json_data['email'].lower(),
                firstname=json_data['firstname'].lower(),
                lastname=json_data['lastname'].lower(),
                password=bcrypt.generate_password_hash(json_data['password']),
                school=json_data['school'].lower())
    db.session.add(user)
    db.session.commit()
    return jsonify("true")


@userblueprint.route('/users/', methods=('GET', ))
@jwt_required
def _get_user():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        if user.is_staff:
            users = User.query.all()
            result = users_schema.dump(users, many=True)
            return jsonify({'users': result})
    return jsonify('forbidden'), 403


@userblueprint.route('/v1/users/login/', methods=('POST', ))
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
                identity=user.username,
                expires_delta=expires)  # Create access token for user
            refresh_token = create_refresh_token(identity=user.username,
                                                 expires_delta=expires)
            return jsonify(access_token=access_token,
                           refresh_token=refresh_token), 200

    return json.dumps({'Login': False}), 500, {
        'ContentType': 'application/json'
    }


@userblueprint.route('/v1/users/refresh/', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    expires = datetime.timedelta(days=30)
    access_token = create_access_token(identity=current_user,
                                       expires_delta=expires)
    return jsonify(access_token=access_token), 200


@userblueprint.route("/v1/users/logout/", methods=["GET"])
@jwt_required
def _logout():
    """Logout the current user."""
    #Could use a blacklist to blacklist tokens but for now we'll wait TODO
    # user = current_user
    # db.session.add(user)
    # db.session.commit()
    # logout_user()


@userblueprint.route("/v1/users/auth/", methods=["GET"])
@jwt_required
def _auth():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if current_user:
        return jsonify(logged_in_as=current_user,
                       user_info={
                           'email': user.email,
                           'school': user.school,
                           'firstname': user.firstname,
                           'lastname': user.lastname,
                           'is_staff': user.is_staff
                       }), 200
    return jsonify(logged_in_as=''), 200


@userblueprint.route("/v1/users/setUserImage/", methods=["POST"])
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


@userblueprint.route("/v1/users/getUserImage/", methods=["GET"])
@jwt_required
def _get_image():

    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        filename = secure_filename(user.profile_image)
        return send_file(os.path.join("image_folder/", filename))

    return jsonify({'message': "Invalid Token"}), 401


@userblueprint.route("/v1/users/changePassword/", methods=['POST'])
@jwt_required
def _change_password():

    json_data = request.get_json()

    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400

    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        password = bcrypt.generate_password_hash(json_data['password'])
        user.password = password
        db.session.commit()
        return jsonify(message="Chang password successful"), 200

    return jsonify({'message': "Invalid Token"}), 401


@userblueprint.route("/v1/users/changeEmail/", methods=['POST'])
@jwt_required
def _change_email():
    json_data = request.get_json()

    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400

    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        email = json_data['email']
        user.email = email
        db.session.commit()
        return jsonify(message="Chang email successful"), 200

    return jsonify({'message': "Invalid Token"}), 401


## SUBJECT SUBSCRIPTION
@userblueprint.route("/v1/users/subscribeToSubject/<int:subjectid>/",
                     methods=['POST'])
@jwt_required
def _subscribe_to_subject(subjectid):
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        subject = Subject.query.filter_by(id=subjectid).first()

        existing_subscription = Subject_Subscription.query.filter_by(
            user_id=user.id, subject_id=subject.id).first()
        if existing_subscription:
            db.session.delete(existing_subscription)
            db.session.commit()
            return jsonify(message="Removed subscription",
                           id=existing_subscription.id,
                           user_id=user.id,
                           subject_id=subject.id), 200

        subject_subscription = Subject_Subscription(user_id=user.id,
                                                    subject_id=subject.id)
        db.session.add(subject_subscription)
        db.session.commit()
        return jsonify(message=True,
                       id=subject_subscription.id,
                       user_id=user.id,
                       subject_id=subject.id), 200

    return jsonify({'message': "Invalid Token"}), 401


@userblueprint.route('/v1/users/getAllSubjectSubscriptions/', methods=['GET'])
@jwt_required
def _get_subject_subscriptions_all():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        is_staff = user.is_staff
        if is_staff:
            subject_subs = Subject_Subscription.query.all()
            result = subjects_subscription_schema.dump(subject_subs, many=True)
            return jsonify({'subject_subs': result}), 200
    return jsonify('forbiden'), 403


@userblueprint.route('/v1/users/getMySubjectSubscriptions/', methods=['GET'])
@jwt_required
def _get_user_subject_subscriptions():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        subject_subs = Subject_Subscription.query.filter_by(user_id=user.id).all()
        result = subjects_subscription_schema.dump(subject_subs, many=True)
        return jsonify(result[0])


## TOPIC SUBSCRIPTION
@userblueprint.route("/v1/users/subscribeToTopic/<int:topicid>/",
                     methods=['POST'])
@jwt_required
def _subscribe_to_topic(topicid):
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        topic = Topic.query.filter_by(id=topicid).first()

        existing_subscription = Topic_Subscription.query.filter_by(
            user_id=user.id, topic_id=topic.id).first()
        if existing_subscription:
            db.session.delete(existing_subscription)
            db.session.commit()
            return jsonify(message="Removed subscription",
                           id=existing_subscription.id,
                           user_id=user.id,
                           topic_id=topic.id), 200

        topic_subscription = Topic_Subscription(user_id=user.id,
                                                topic_id=topic.id)
        db.session.add(topic_subscription)
        db.session.commit()
        return jsonify(message=True,
                       id=topic_subscription.id,
                       user_id=user.id,
                       topic_id=topic.id), 200

    return jsonify({'message': "Invalid Token"}), 401


@userblueprint.route('/v1/users/getAllTopicSubscriptions/', methods=['GET'])
@jwt_required
def _get_topic_subscriptions_all():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        is_staff = user.is_staff
        if is_staff:
            topic_subs = Topic_Subscription.query.all()
            result = topics_subscription_schema.dump(topic_subs, many=True)
            return jsonify({'topic_subs': result}), 200
    return jsonify('forbiden'), 403


@userblueprint.route('/v1/users/getTopicSubscription/<int:topicid>/',
                     methods=['GET'])
@jwt_required
def _get_topic_subscription(topicid):
    topic_sub = Topic_Subscription.query.filter_by(topic_id=topicid).first()
    result = topics_subscription_schema.dump(topic_sub, many=False)
    return jsonify(result[0])


@userblueprint.route('/v1/users/getMyTopicSubscriptions/', methods=['GET'])
@jwt_required
def _get_user_topic_subscription():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        topic_subs = Topic_Subscription.query.filter_by(user_id=user.id).all()
        result = topics_subscription_schema.dump(topic_subs, many=True)
        return jsonify(result[0])
