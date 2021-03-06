from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length

class TopicCreation(FlaskForm):
    topic = StringField("Topic Name", validators=[DataRequired(), Length(max=50)])
    description = StringField("Description", validators=[DataRequired(), Length(max=200)])

class SubjectCreation(FlaskForm):
    subject = StringField("Subject Name", validators=[DataRequired(), Length(max=50)])
    description = StringField("Description", validators=[DataRequired(), Length(max=200)])

class PostCreation(FlaskForm):
    resource = StringField("Resource Name", validators=[DataRequired(), Length(max=50)])
    description = StringField("Description", validators=[DataRequired(), Length(max=200)])