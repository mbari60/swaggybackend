from flask_restful import Resource, marshal
from flask_jwt_extended import jwt_required
from models import UserModel
from resources.users import user_fields
from admin.onlyadmin import admin_required

class adminUsers(Resource):
    # admin will use this to get all users 
    @jwt_required()
    @admin_required
    def get(self):
        users = UserModel.query.all()
        if users:
            return marshal(users, user_fields), 200
        else:
            return {"message": "No users found"}, 404
