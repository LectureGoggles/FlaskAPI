# user/views.py
from flask import Blueprint, request, send_file, jsonify, json, flash
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, jwt_refresh_token_required, create_refresh_token
from marshmallow import ValidationError
from werkzeug.utils import secure_filename

from app.extensions import db, bcrypt
from .forms import LoginForm
from .models import User, Subject_Subscription, Topic_Subscription
from app.post.models import Subject, Topic, Post
from .schema import user_schema, users_schema
from .schema import subjects_subscription_schema
from .schema import topics_subscription_schema

import os
import datetime
from urllib.parse import urlparse

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

userblueprint = Blueprint('user', __name__)


@userblueprint.route('/v1/users/signup/', methods=('POST', ))
def _register_user():

    json_data = request.get_json()

    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400

    try:
        user_schema.load(json_data)
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
    user.is_teacher = json_data['is_teacher']
    db.session.add(user)
    db.session.commit()
    return jsonify(message="Successful user creation", username=user.username)


@userblueprint.route('/v1/users/delete/', methods=['POST'])
@jwt_required
def _delete_user():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()

        User.query.filter_by(id=user.id).delete()
        #User.query.filter(User.id == 123).delete()
        db.session.commit()
        return jsonify(message="Successful account deletion"), 200

    return jsonify(message="Invalid token")


@userblueprint.route('/users/', methods=('GET', ))
@jwt_required
def _get_user():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        if user.is_staff:
            users = User.query.all()
            # HACK: Super hacky, will be removed when front end is updated
            dump = users_schema.dump(users, many=True)
            result = list()
            result.append(dump)
            result.append(dict())
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
    json_data = request.get_json()

    if current_user:
        user = User.query.filter_by(username=current_user).first()
        if user:
            if (urlparse(json_data['url']).scheme == 'http'
                    or urlparse(json_data['url']).scheme == 'https'):
                user.profile_image = json_data['url']
                user_posts = Post.query.filter_by(author_id=user.id).all()
                for user_post in user_posts:
                    user_post.author_image = json_data['url']
                db.session.commit()
                return jsonify('successfully changed image'), 200
            if (json_data['url'] == ''):
                user.profile_image = 'Avatar.svg'
                user_posts = Post.query.filter_by(author_id=user.id).all()
                for user_post in user_posts:
                    user_post.author_image = 'Avatar.svg'
                db.session.commit()
                return jsonify('successfully changed image to default'), 200
            return jsonify('invalid format'), 415
        return jsonify('not found'), 404
    return jsonify('forbidden'), 403


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
        return jsonify(message="Change password successful"), 200

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
            # HACK: Super hacky, will be removed when front end is updated
            dump = subjects_subscription_schema.dump(subject_subs, many=True)
            result = list()
            result.append(dump)
            result.append(dict())
            return jsonify({'subject_subs': result}), 200
    return jsonify('forbidden'), 403


@userblueprint.route('/v1/users/getMySubjectSubscriptions/', methods=['GET'])
@jwt_required
def _get_user_subject_subscriptions():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        subject_subs = Subject_Subscription.query.filter_by(
            user_id=user.id).all()
        # HACK: Super hacky, will be removed when front end is updated
        dump = subjects_subscription_schema.dump(subject_subs, many=True)
        result = list()
        result.append(dump)
        result.append(dict())
        try:
            return jsonify(result[0])
        except:
            return jsonify([])

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
            # HACK: Super hacky, will be removed when front end is updated
            dump = topics_subscription_schema.dump(topic_subs, many=True)
            result = list()
            result.append(dump)
            result.append(dict())
            return jsonify({'topic_subs': result}), 200
    return jsonify('forbidden'), 403


@userblueprint.route('/v1/users/getTopicSubscription/<int:topicid>/',
                     methods=['GET'])
@jwt_required
def _get_all_topic_subscription(topicid):
    """Gets all of the users subscribed to the topic subscription if you are an admin."""
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        if user.is_staff:
            topic_sub = Topic_Subscription.query.filter_by(
                topic_id=topicid).first()
            # HACK: Super hacky, will be removed when front end is updated
            dump = topics_subscription_schema.dump(topic_sub, many=False)
            result = list()
            result.append(dump)
            result.append(dict())
            try:
                return jsonify(result[0])
            except:
                return jsonify([])
        return jsonify('unauthorized'), 403
    return jsonify('unauthorized'), 401


@userblueprint.route('/v1/users/getMyTopicSubscription/<int:topicid>/',
                     methods=['GET'])
@jwt_required
def _get_topic_subscription(topicid):
    """Given a topic id, return the subscription status of the topic."""
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        if user:
            topic_sub = Topic_Subscription.query.filter_by(
                topic_id=topicid, user_id=user.id).first()
            # HACK: Super hacky, will be removed when front end is updated
            dump = topics_subscription_schema.dump(topic_sub, many=False)
            result = list()
            result.append(dump)
            result.append(dict())
            try:
                return jsonify(result[0])
            except:
                return jsonify([])
        return jsonify('unauthorized'), 403
    return jsonify('unauthorized'), 401


@userblueprint.route('/v1/users/getMyTopicSubscriptions/', methods=['GET'])
@jwt_required
def _get_user_topic_subscription():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        topic_subs = Topic_Subscription.query.filter_by(user_id=user.id).all()
        # HACK: Super hacky, will be removed when front end is updated
        dump = topics_subscription_schema.dump(topic_subs, many=True)
        result = list()
        result.append(dump)
        result.append(dict())
        try:
            return jsonify(result[0])
        except:
            return jsonify([])
