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
        fields = ('resource', 'resource_url', 'description', 'id', 'created_at')

post_schema = PostSchema()
posts_schema = PostSchema(many=True)

class UpvotePostSchema(ma.ModelSchema):
    class Meta:
        model = UpvotePost
        fields = ('id', 'user_id', 'vote_choice')

upvote_schema = UpvotePostSchema()
upvotes_schema = UpvotePostSchema(many=True)

class ReportSchema(ma.ModelSchema):
    class Meta:
        model = Report
        fields = ('id', 'description', 'reported_post_id', 'resolved_by')

report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)