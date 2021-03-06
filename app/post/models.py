from app.extensions import db
import datetime as dt


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    subject_image = db.Column(db.String(2084), nullable=False, default="default_subject.png")

    # Relation with topic
    addresses = db.relationship('Topic', backref='subjects', lazy=True)


class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    topic_image = db.Column(db.String(2084), nullable=False, default="default_subject.jpg")

    # Relation with subject and post
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    posts = db.relationship('Post', backref='topics', lazy=True)
    

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resource = db.Column(db.String(100), nullable=False)
    resource_url = db.Column(db.String(2084), nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    topic_name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(400), nullable=False)
    upvote = db.Column(db.Integer, default=0)
    upvote_count = db.Column(db.Integer, default=0)
    post_image = db.Column(db.String(2084), nullable=False, default='Image.svg')
    author_image = db.Column(db.String(2084), nullable=False, default='Avatar.svg')
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    # Relation with topic
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    upvoteposts = db.relationship('UpvotePost', backref='posts', lazy=True)


class UpvotePost(db.Model):
    __tablename__ = 'upvoteposts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    vote_choice = db.Column(db.Integer, nullable=False)


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    reported_post_id = db.Column(db.Integer, nullable=True)
    reported_content_extension = db.Column(db.String(200), nullable=True)
    resolved = db.Column(db.Boolean, default=False)
    resolved_by = db.Column(db.String(100), default="unsolved")
    teacher_created = db.Column(db.Boolean, default=False)