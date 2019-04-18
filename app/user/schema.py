from app.extensions import ma
from .models import User, Subject_Subscription, Topic_Subscription


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        fields = ('username', 'email', 'firstname', 'lastname', 'password', 'school', 'id')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class SubjectSubscriptionSchema(ma.ModelSchema):
    class Meta:
        model = Subject_Subscription
        fields = ('id', 'user_id', 'subject_id')


subject_subscription_schema = SubjectSubscriptionSchema()
subjects_subscription_schema = SubjectSubscriptionSchema(many=True)


class TopicSubscriptionSchema(ma.ModelSchema):
    class Meta:
        model = Topic_Subscription
        fields = ('id', 'user_id', 'topic_id')


topic_subscription_schema = TopicSubscriptionSchema()
topics_subscription_schema = TopicSubscriptionSchema(many=True)