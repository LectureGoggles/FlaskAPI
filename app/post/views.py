from flask import Blueprint, request, redirect, send_file
from flask_jwt_extended import jwt_required, jwt_optional, create_access_token, get_jwt_identity
from flask import jsonify, json, render_template, flash, redirect, request
from marshmallow import ValidationError
from werkzeug.utils import secure_filename

from app.extensions import db, login_manager, bcrypt
from .forms import SubjectCreation, TopicCreation, PostCreation
from .models import Subject, Topic, Post, Report, UpvotePost
from app.user.models import User
from .schema import SubjectSchema, subject_schema, subjects_schema
from .schema import TopicSchema, topic_schema, topics_schema
from .schema import PostSchema, post_schema, posts_schema
from .schema import ReportSchema, report_schema, reports_schema
from .schema import UpvotePostSchema, upvote_schema, upvotes_schema
import os

postblueprint = Blueprint('post', __name__)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

### SUBJECT
@postblueprint.route('/v1/subject/createSubject', methods=['POST',])
@jwt_required
def _subjectcreate():
    
    json_data = request.get_json()

    try:
        subject_data = subject_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # check for subject already created
    duplicatesubject = Subject.query.filter_by(subject=json_data['subject'].lower()).first()
    if duplicatesubject:
        return jsonify({"message": "Duplicate subject"}), 400

    # Check to see if subject exists
    current_user = get_jwt_identity()
    if current_user is not None:
        user = User.query.filter_by(username=current_user).first()
        subject = Subject(
            subject=json_data['subject'].lower(),
            description=json_data['description'].lower(),
            author_id=user.id
        )
        db.session.add(subject)
        db.session.commit()
        return jsonify(message=True,
                       id=subject.id,
                       name=subject.subject), 200
    
    return jsonify({"message": "Fail"}), 400

@postblueprint.route('/v1/subject/getAll', methods=['GET'])
def _getsubjectall():
    subjects = Subject.query.all()
    result = subjects_schema.dump(subjects, many=True)
    return jsonify({'subjects': result})

@postblueprint.route('/v1/subject/search/<subjectstr>', methods=['GET'])
def _getsubject(subjectstr):
    getsubject = Subject.query.filter_by(subject=subjectstr.lower()).first()

    if getsubject:
        return jsonify(subject_id=getsubject.id, 
                       subject_name=getsubject.subject, 
                       subject_description=getsubject.description, 
                       success='True', code=200)
    else:
        return jsonify({"message": "Subject does not found"}), 400

@postblueprint.route("/v1/subject/setSubjectImageOn/<int:subjectid>", methods=["POST"])
@jwt_required
def _set_subject_image(subjectid):

    current_user = get_jwt_identity()

    if current_user:
        subject = Subject.query.filter_by(id=subjectid).first()
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
            subject.subject_image = filename.lower()
            db.session.commit()
            return jsonify({'message': True}), 200

    return json({'message': False}), 400

@postblueprint.route("/v1/subject/getSubjectImageOn/<int:subjectid>", methods=["GET"])
def _get_subject_image(subjectid):

    subject = Subject.query.filter_by(id=subjectid).first()
    if subject:
        filename = secure_filename(subject.subject_image)
        return send_file(os.path.join("image_folder/", filename)) 

    return jsonify({'message': "No subject of id provided"}), 400

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




### TOPIC
@postblueprint.route('/v1/topic/createTopic/<int:subjectid>/', methods=['POST',])
@jwt_required
def _posttopic(subjectid):
    json_data = request.get_json()

    try:
        topic_data = topic_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # check for post already created
    duplicatetopic = Topic.query.filter_by(topic=json_data['topic'].lower()).first()
    if duplicatetopic:
        return jsonify({"message": "Duplicate post"}), 400

    # is this a valid subject
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        topic = Topic(
            topic=json_data['topic'].lower(),
            description=json_data['description'].lower(),
            author_id=user.id,
            subject_id=subjectid
        )
        db.session.add(topic)
        db.session.commit()
        return jsonify(message=True,
                       id=topic.id,
                       name=topic.topic), 200

    return jsonify({"message": "Fail"}), 400

@postblueprint.route('/v1/topic/getTopics/<int:subjectid>/', methods=['GET',])
def _gettopicall(subjectid):

    topics = Topic.query.filter_by(subject_id=subjectid).all()
    result = topics_schema.dump(topics, many=True)
    return jsonify({'topics': result})

@postblueprint.route("/v1/topic/setTopicImageOn/<int:topicid>", methods=["POST"])
@jwt_required
def _set_topic_image(topicid):

    current_user = get_jwt_identity()

    if current_user:
        topic = Topic.query.filter_by(id=topicid).first()
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
            topic.topic_image = filename.lower()
            db.session.commit()
            return jsonify({'message': True}), 200

    return json({'message': False}), 400

@postblueprint.route("/v1/topic/getTopicImageOn/<int:topicid>", methods=["GET"])
def _get_topic_image(topicid):

    topic = Topic.query.filter_by(id=topicid).first()
    if topic:
        filename = secure_filename(topic.topic_image)
        return send_file(os.path.join("image_folder/", filename)) 

    return jsonify({'message': "No topic of id provided"}), 400

### POST
@postblueprint.route('/v1/post/createPost/<int:topicid>/', methods=['POST',])
@jwt_required
def _postcreate(topicid):

    json_data = request.get_json()

    try:
        post_data = post_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # check for post already created
    duplicatepost = Post.query.filter_by(resource=json_data['resource'].lower()).first()
    if duplicatepost:
        return jsonify({"message": "Duplicate post"}), 400

    # is this a valid resource
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        _author_name = User.query.filter_by(id=user.id).first()
        _topic_name = Topic.query.filter_by(id=topicid).first()
        _subject_name = Subject.query.filter_by(id=_topic_name.subject_id).first()
        _subject_id = _subject_name
        post = Post(
            resource=json_data['resource'].lower(),
            resource_url=json_data['resource_url'].lower(),
            description=json_data['description'].lower(),
            author_id=user.id,
            topic_id=topicid,
            author_name=_author_name.username,
            topic_name=_topic_name.topic,
            subject_name=_subject_name.subject,
            subject_id=_subject_id.id,
            author_image=_author_name.profile_image,

        )
        db.session.add(post)
        db.session.commit()
        return jsonify(message=True,
                       id=post.id), 200

    return jsonify({"message": "Fail"}), 400


@postblueprint.route('/v1/post/getTopic/<int:topicid>/', methods=['GET',])
def _getpostalltopic(topicid):
    posts = Post.query.filter_by(topic_id=topicid).all()
    result = posts_schema.dump(posts, many=True)
    return jsonify({'posts': result})


@postblueprint.route("/v1/post/setTopicImageOn/<int:postid>", methods=["POST"])
@jwt_required
def _set_post_image(postid):

    current_user = get_jwt_identity()

    if current_user:
        post = Post.query.filter_by(id=postid).first()
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
            post.post_image = filename.lower()
            db.session.commit()
            return jsonify({'message': True}), 200

    return json({'message': False}), 400

@postblueprint.route("/v1/topic/getPostImageOn/<int:postid>", methods=["GET"])
def _get_post_image(postid):

    post = Post.query.filter_by(id=postid).first()
    if post:
        filename = secure_filename(post.post_image)
        return send_file(os.path.join("image_folder/", filename)) 

    return jsonify({'message': "No topic of id provided"}), 400


@postblueprint.route('/v1/post/getAll', methods=['GET',])
@jwt_optional
def _get_post_all():

    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        votes = UpvotePost.query.filter_by(user_id=user.id).all()

        # return all posts and all user votes on post
        posts = Post.query.all()
        posts_result = posts_schema.dump(posts, many=True)
        vote_status = upvote_schema.dump(votes, many=True)
        return jsonify(post=posts_result, vote_status=vote_status)


    # no user token, return posts
    posts = Post.query.all()
    posts_result = posts_schema.dump(posts, many=True)
    return jsonify(post=posts_result)


def _get_post_int(postid):
    return 0


@postblueprint.route('/v1/post/get/<int:postid>', methods=['GET'])
@jwt_optional
def _get_post_id(postid):

    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        vote = UpvotePost.query.filter_by(user_id=user.id, post_id=postid).first()
        if vote:  # Vote found for provided user
            post = Post.query.filter_by(id=postid).first()
            post_result = post_schema.dump(post)
            vote_status = upvote_schema.dump(vote)
            return jsonify(post=post_result, vote_status=vote_status)
        # No vote found for provided user
        post = Post.query.filter_by(id=postid).first()
        post_result = post_schema.dump(post)
        return jsonify({'post': post_result}, {'vote_status': "None"})

    # No jwt provided
    post = Post.query.filter_by(id=postid).first()
    post_result = post_schema.dump(post)
    return jsonify({'post': post_result})


@postblueprint.route('/v1/post/deletePost/<int:postid>', methods=['POST'])
@jwt_required
def _deletepost(postid):

    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        post = Post.query.filter_by(id=postid).first()
        if user.id == post.author_id:
            if post:
                db.session.delete(post)
                db.session.commit()
                return jsonify(message="post deleted"), 200
            return jsonify(message="post id provided not found"), 400
        return jsonify(message="user did not create this post"), 400
    return jsonify(message="not valid token"), 400

  
@postblueprint.route('/v1/post/getMyPosts', methods=['GET',])
@jwt_required
def _getMyPosts():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        posts = Post.query.filter_by(author_id=user.id).all()
        posts_result = posts_schema.dump(posts, many=True)
        return jsonify({'posts': posts_result})
    return jsonify(message="invalid token"), 401

  
### REPORTS

@postblueprint.route('/v1/report/createReport/<int:postid>/', methods=['POST',])
@jwt_optional
def _createreport(postid):
    json_data = request.get_json()

    try:
        report_data = report_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    #is this a valid subject
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        report = Report(
            description=json_data['description'].lower(),
            reported_post_id=postid,
            author_id=user.id,
        )
        db.session.add(report)
        db.session.commit()
        return jsonify({"message": "Success"}), 200
    else:
        user = User.query.filter_by(username=current_user).first()
        report = Report(
            description=json_data['description'].lower(),
            reported_post_id=postid,
        )
        db.session.add(report)
        db.session.commit()
        return jsonify({"message": "Success"}), 200

    return jsonify({"message": "Fail"}), 400

@postblueprint.route('/v1/report/getPostReport/<int:postid>/', methods=['GET',])
def _getpostreports(postid):
    reports = Report.query.filter_by(reported_post_id=postid).all()
    result = reports_schema.dump(reports, many=True)
    return jsonify({'reports': result})

@postblueprint.route('/v1/report/getReports', methods=['GET',])
def _getreportsall():
    reports = Report.query.all()
    result = reports_schema.dump(reports, many=True)
    return jsonify({'reports': result})

## POST VOTING
@postblueprint.route('/v1/vote/upvotePost/<int:postid>/', methods=['POST'])
@jwt_required
def _upvote_post(postid):

    #is this a valid subject
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        upvote_post = UpvotePost.query.filter_by(user_id=user.id, post_id=postid).first()
        # check if user has already upvoted post
        if upvote_post:
            # did he upvote or downvote
            if upvote_post.vote_choice == 1:
                upvote_post.vote_choice = 0
                current_post = Post.query.filter_by(id=postid).first()
                current_post.upvote_count -= 1
                db.session.commit()
                return jsonify({"message": "Success"}), 200
            if upvote_post.vote_choice == 0:
                upvote_post.vote_choice = 1
                current_post = Post.query.filter_by(id=postid).first()
                current_post.upvote_count += 1
                db.session.commit()
                return jsonify({"message": "Success"}), 200
            # this user has created a downvote for this post. Change that downvote to an upvote
            upvote_post.vote_choice = 1
            current_post = Post.query.filter_by(id=postid).first()
            current_post.upvote_count += 2
            db.session.commit()
            return jsonify({"message": "Success"}), 200
        else:
            # vote doesn't exist yet so create a upvote
            current_post = Post.query.filter_by(id=postid).first()
            current_post.upvote_count += 1
            upvote = UpvotePost(
                post_id=postid,
                user_id=user.id,
                vote_choice=1
            )
            db.session.add(upvote)
            db.session.commit()
            return jsonify({"message": "Success"}), 200

    return jsonify({"message": "Invalid current user token"}), 400

@postblueprint.route('/v1/vote/downvotePost/<int:postid>/', methods=['POST'])
@jwt_required
def _downvote_post(postid):

    #is this a valid subject
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        upvote_post = UpvotePost.query.filter_by(user_id=user.id, post_id=postid).first()
        # check if user has already upvoted post
        if upvote_post:
            # did he upvote or downvote
            if upvote_post.vote_choice == -1:
                upvote_post.vote_choice = 0
                current_post = Post.query.filter_by(id=postid).first()
                current_post.upvote_count += 1
                db.session.commit()
                return jsonify({"message": "Success"}), 200
            if upvote_post.vote_choice == 0:
                upvote_post.vote_choice = 1
                current_post = Post.query.filter_by(id=postid).first()
                current_post.upvote_count -= 1
                db.session.commit()
                return jsonify({"message": "Success"}), 200
            # this user has created an upvote for this post. Change that upvote to a downvote
            upvote_post.vote_choice = -1
            current_post = Post.query.filter_by(id=postid).first()
            current_post.upvote_count -= 2
            db.session.commit()
            return jsonify({"message": "Success"}), 200

        else:
            # vote doesn't exist yet so create a upvote
            current_post = Post.query.filter_by(id=postid).first()
            current_post.upvote_count -= 1
            upvote = UpvotePost(
                post_id=postid,
                user_id=user.id,
                vote_choice=-1
            )
            db.session.add(upvote)
            db.session.commit()
            return jsonify({"message": "Success"}), 200

    return jsonify({"message": "Invalid current user token"}), 400

@postblueprint.route('/v1/vote/getVotesOnPost/<int:postid>', methods=['GET'])
def _getpostvotes(postid):
    votes = UpvotePost.query.filter_by(post_id=postid).all()
    result = upvotes_schema.dump(votes, many=True)
    return jsonify({'reports': result})

# We will want to only allow users with the role of admin for this
@postblueprint.route('/v1/vote/getAllVotes', methods=['GET'])
@jwt_required
def _getvotesall():
    votes = UpvotePost.query.all()
    result = upvotes_schema.dump(votes, many=True)
    return jsonify({'votes': result})