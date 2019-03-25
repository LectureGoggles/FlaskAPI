from app.extensions import ma
from .models import User

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        fields = ('username', 'email', 'firstname', 'lastname', 'password', 'school', 'id')
        
user_schema = UserSchema()
users_schema = UserSchema(many=True)

