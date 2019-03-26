from app.extensions import ma
from .models import Subject, Topic, Post, Report

class SubjectSchema(ma.ModelSchema):
    class Meta:
        model = Subject
        fields = ('subject', 'description', 'id')

subject_schema = SubjectSchema()
subjects_schema = SubjectSchema(many=True)    


class TopicSchema(ma.ModelSchema):
    class Meta:
        model = Topic
        fields = ('subject', 'description', 'id')

topic_schema = TopicSchema()
topics_schema = TopicSchema(many=True)


class PostSchema(ma.ModelSchema):
    class Meta:
        model = Post
        fields = ('subject', 'description', 'id')

post_schema = PostSchema()
posts_schema = PostSchema(many=True)

class ReportSchema(ma.ModelSchema):
    class Meta:
        model = Report
        fields = ('id', 'description', 'reported_post_id', 'resolved_by')

report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)