from app.extensions import ma
from .models import Subject, Topic, Post, Report, UpvotePost


class SubjectSchema(ma.ModelSchema):
    class Meta:
        model = Subject
        fields = ('subject', 'description', 'id')


subject_schema = SubjectSchema()
subjects_schema = SubjectSchema(many=True)


class TopicSchema(ma.ModelSchema):
    class Meta:
        model = Topic
        fields = ('topic', 'description', 'id')


topic_schema = TopicSchema()
topics_schema = TopicSchema(many=True)


class PostSchema(ma.ModelSchema):
    class Meta:
        model = Post
        fields = ('resource', 'resource_url', 'description', 'id', 'created_at', 'upvote_count', 'subject_name', 'author_name', 'topic_name', 'subject_id', 'author_image', 'post_image', 'topic_id')


post_schema = PostSchema()
posts_schema = PostSchema(many=True)


class UpvotePostSchema(ma.ModelSchema):
    class Meta:
        model = UpvotePost
        fields = ('id', 'post_id', 'user_id', 'vote_choice')


upvote_schema = UpvotePostSchema()
upvotes_schema = UpvotePostSchema(many=True)


class ReportSchema(ma.ModelSchema):
    class Meta:
        model = Report
        fields = ('id', 'description', 'reported_content_extension', 'author_id', 'resolved', 'resolved_by', 'teacher_created', 'created_at', 'reported_post_id')


report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)