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
from urllib.parse import urlparse

postblueprint = Blueprint('post', __name__)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

### SUBJECT
@postblueprint.route('/v1/subject/createSubject/', methods=['POST',])
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

@postblueprint.route('/v1/subject/getAll/', methods=['GET'])
def _getsubjectall():
    subjects = Subject.query.all()
    result = subjects_schema.dump(subjects, many=True)
    return jsonify({'subjects': result})


@postblueprint.route('/v1/subject/getById/<int:subjectid>/', methods=['GET'])
def _get_subject_by_id_(subjectid):
    subject = Subject.query.filter_by(id=subjectid).first()
    if (subject):
        result = subjects_schema.dump(subject, many=False)
        return jsonify({'subject': result})
    return jsonify({'subject': None}), 404

@postblueprint.route('/v1/subject/search/<subjectstr>/', methods=['GET'])
def _getsubject(subjectstr):
    getsubject = Subject.query.filter_by(subject=subjectstr.lower()).first()

    if getsubject:
        return jsonify(subject_id=getsubject.id, 
                       subject_name=getsubject.subject, 
                       subject_description=getsubject.description, 
                       success='True', code=200)
    else:
        return jsonify({"message": "Subject does not found"}), 400

@postblueprint.route("/v1/subject/setSubjectImageOn/<int:subjectid>/", methods=["POST"])
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

@postblueprint.route("/v1/subject/getSubjectImageOn/<int:subjectid>/", methods=["GET"])
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

@postblueprint.route("/v1/topic/setTopicImageOn/<int:topicid>/", methods=["POST"])
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


@postblueprint.route("/v1/topic/getById/<int:topicid>/", methods=["GET"])
def _get_topic(topicid):
    topic = Topic.query.filter_by(id=topicid).first()
    if topic:
        subject = Subject.query.filter_by(id=topic.subject_id).first()
        if subject:
            subject_result = subjects_schema.dump(subject, many=False)
            topic_result = topics_schema.dump(topic, many=False)
            return jsonify({'subject': subject_result[0], 'topic': topic_result[0]})
    return jsonify('not found'), 404


@postblueprint.route("/v1/topic/getTopicImageOn/<int:topicid>/", methods=["GET"])
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
            resource_url=json_data['resource_url'],
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


@postblueprint.route('/v1/post/getTopic/<int:topicid>/', methods=['GET'])
def _getpostalltopic(topicid):

    posts = Post.query.filter_by(topic_id=topicid).all()
    result = posts_schema.dump(posts, many=True)
    return jsonify({'posts': result})


@postblueprint.route("/v1/post/setPostmageOn/<int:postid>/", methods=["POST"])
@jwt_required
def _set_post_image(postid):

    current_user = get_jwt_identity()
    json_data = request.get_json()

    if current_user:
        post = Post.query.filter_by(id=postid).first()
        if post:
            print(urlparse(json_data['url']))
            if (urlparse(json_data['url']).scheme == 'http' or urlparse(json_data['url']).scheme == 'https'):
                post.post_image = json_data['url']
                db.session.commit()
                return jsonify('successfully changed image'), 200
            if (json_data['url'] == ''):
                post.post_image = 'Image.svg'
                db.session.commit()
                return jsonify('successfully changed image to default'), 200
            return jsonify('invalid format'), 415
        return jsonify('not found'), 404
    return jsonify('forbidden'), 403

@postblueprint.route("/v1/topic/getPostImageOn/<int:postid>/", methods=["GET"])
def _get_post_image(postid):

    post = Post.query.filter_by(id=postid).first()
    if post:
        return jsonify({'url': post.post_image}), 200

    return jsonify({'message': "No topic of id provided"}), 400


@postblueprint.route('/v1/post/getAll/', methods=['GET',])
@jwt_optional
def _get_post_all():

    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        votes = UpvotePost.query.filter_by(user_id=user.id).all()

        # return all posts and all user votes on post
        posts = Post.query.order_by(Post.upvote_count.desc()).all()
        posts_result = posts_schema.dump(posts, many=True)
        vote_status = upvote_schema.dump(votes, many=True)
        return jsonify(posts=posts_result, vote_status=vote_status)


    # no user token, return posts
    posts = Post.query.order_by(Post.upvote_count.desc()).all()
    posts_result = posts_schema.dump(posts, many=True)
    return jsonify(posts=posts_result)


def _get_post_int(postid):
    return 0


@postblueprint.route('/v1/post/get/<int:postid>/', methods=['GET'])
@jwt_optional
def _get_post_id(postid):

    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        vote = UpvotePost.query.filter_by(user_id=user.id, post_id=postid).first()
        if vote:  # Vote found for provided user
            posts = Post.query.filter_by(id=postid).first()
            post_result = post_schema.dump(posts)
            vote_status = upvote_schema.dump(vote)
            return jsonify(posts=post_result, vote_status=vote_status)
        # No vote found for provided user
        post = Post.query.filter_by(id=postid).first()
        post_result = post_schema.dump(post)
        return jsonify({'posts': post_result}, {'vote_status': "None"})

    # No jwt provided
    post = Post.query.filter_by(id=postid).first()
    post_result = post_schema.dump(post)
    return jsonify({'posts': post_result})



@postblueprint.route('/v1/post/deletePost/<int:postid>/', methods=['POST'])
@jwt_required
def _deletepost(postid):

    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        post = Post.query.filter_by(id=postid).first()
        upvotes = UpvotePost.query.filter_by(post_id=postid).all()
        if user.id == post.author_id or user.is_staff:
            if post:
                for upvote in upvotes:
                    db.session.delete(upvote)
                db.session.commit()
                db.session.delete(post)
                db.session.commit()
                return jsonify(message="post deleted"), 200
            return jsonify(message="post id provided not found"), 400
        return jsonify(message="user did not create this post"), 400
    return jsonify(message="not valid token"), 400


@postblueprint.route('/v1/post/getMyPosts/', methods=['GET',])
@jwt_required
def _getMyPosts():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        posts = Post.query.order_by(Post.upvote_count.desc()).filter_by(author_id=user.id).all()
        posts_result = posts_schema.dump(posts, many=True)
        return jsonify({'posts': posts_result})
    return jsonify(message="invalid token"), 401

  
### REPORTS

@postblueprint.route('/v1/report/createReportGeneral/', methods=['POST'])
@jwt_optional
def _create_report_general():
    json_data = request.get_json()

    try:
        report_data = report_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422
    
    # Validate passed extension information
    reported_extension = json_data['extension']

    if reported_extension[0] == '/':
        if reported_extension[len(reported_extension)-1]:
            print()
        else:
            return jsonify(message="invalid extension, make sure the last letter is '/'"), 400
    else:
        return jsonify(message="invalid extension, make sure the first letter is '/'"), 400

    current_user = get_jwt_identity()
    # if valid jwt was given
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        report = Report(
            description=json_data['description'],
            reported_content_extension=json_data['extension'],
            author_id=user.id,
        )
        if user.is_teacher:
            report.teacher_created = True
        
        db.session.add(report)
        db.session.commit()
        return jsonify(message="success"), 200
    else:
        #jwt is optional
        report = Report(
            description=json_data['description'],
            reported_content_extension=json_data['extension']
        )
        return jsonify(message="success"), 200
    return jsonify(message="unauthorized"), 403


@postblueprint.route('/v1/report/createReportPost/<int:postid>', methods=['POST'])
@jwt_optional
def _create_report_post(postid):
    json_data = request.get_json()

    try:
        report_data = report_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422
    
    current_user = get_jwt_identity()
    # if valid jwt was given
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        report = Report(
            description=json_data['description'],
            reported_post_id=postid,
            author_id=user.id,
        )
        if user.is_teacher:
            report.teacher_created = True
        
        db.session.add(report)
        db.session.commit()
        return jsonify(message="success"), 200
    else:
        #jwt is optional
        report = Report(
            description=json_data['description'],
            reported_post_id=postid
        )
        return jsonify(message="success"), 200
    return jsonify(message="unauthorized"), 403


@postblueprint.route('/v1/report/getPostReport/<int:postid>/', methods=['GET'])
@jwt_required
def _getpostreports(postid):
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        is_staff = user.is_staff
        if is_staff:
            reports = Report.query.filter_by(reported_post_id=postid).all()
            result = reports_schema.dump(reports, many=True)
            return jsonify({'reports': result})
    return jsonify('unauthorized'), 403


@postblueprint.route('/v1/report/getReports/', methods=['GET'])
@jwt_required
def _getreportsall():

    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        is_staff = user.is_staff
        if is_staff:
            reports = Report.query.filter_by(resolved=False).all()
            result = reports_schema.dump(reports, many=True)
            return jsonify({'reports': result})
    return jsonify('unauthorized'), 403

@postblueprint.route('/v1/report/resolveReport/<int:reportid>', methods=['POST'])
@jwt_required
def _resolve_report(reportid):
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        is_staff = user.is_staff
        if is_staff:
            # check if report exists
            report = Report.query.filter_by(id=reportid).first()
            if report:
                report.resolved = True
                return jsonify(message="Report successfully resolved"), 200
    
    return jsonify('forbidden'), 403

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
                upvote_post.vote_choice = -1
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

@postblueprint.route('/v1/vote/getVotesOnPost/<int:postid>/', methods=['GET'])
def _getpostvotes(postid):
    votes = UpvotePost.query.filter_by(post_id=postid).all()
    result = upvotes_schema.dump(votes, many=True)
    return jsonify({'reports': result})

# We will want to only allow users with the role of admin for this
@postblueprint.route('/v1/vote/getAllVotes/', methods=['GET'])
@jwt_required
def _getvotesall():
    votes = UpvotePost.query.all()
    result = upvotes_schema.dump(votes, many=True)
    return jsonify({'votes': result})